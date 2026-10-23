import bpy,json
from pathlib import Path
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall']
# Expand the limestone field onto the GIS shell's east-facing flanking wings.
env=bpy.data.objects['HAAS_Corrected_GIS_Wall_Envelope']
stone=bpy.data.materials['HAAS_Photo_Limestone']
if all(m.name!=stone.name for m in env.data.materials): env.data.materials.append(stone)
stone_idx=next(i for i,m in enumerate(env.data.materials) if m and m.name==stone.name)
facade_faces=[]
for p in env.data.polygons:
    n=env.matrix_world.to_3x3()@p.normal; co=env.matrix_world@p.center
    if n.x>0.95 and co.x>1.5 and co.z>0.4:
        p.material_index=stone_idx;facade_faces.append(p.index)
# Warm the stone, reduce overly high contrast and bring brick out of near-black.
for n in stone.node_tree.nodes:
    if n.type=='BSDF_PRINCIPLED':
        n.inputs['Base Color'].default_value=(0.76,0.65,0.50,1);n.inputs['Roughness'].default_value=0.88
stone.diffuse_color=(0.76,0.65,0.50,1)
for mname in ['Purdue_Red_Brick','Purdue_Red_Brick.001','HAAS_R6_Red_Brick_Inlay']:
    m=bpy.data.materials.get(mname)
    if not m or not m.node_tree: continue
    m.diffuse_color=(0.36,0.095,0.045,1)
    for node in m.node_tree.nodes:
        if node.type=='TEX_BRICK':
            node.inputs['Color1'].default_value=(0.40,0.10,0.050,1)
            node.inputs['Color2'].default_value=(0.28,0.060,0.026,1)
            node.inputs['Mortar'].default_value=(0.16,0.09,0.055,1)
# Continue source-derived brick surrounds onto the east wing windows, at the GIS wall face.
brick=bpy.data.materials['HAAS_R6_Red_Brick_Inlay']
verts=[];faces=[]
def quad(x,y0,y1,z0,z1):
    i=len(verts);verts.extend([(x,y0,z0),(x,y1,z0),(x,y1,z1),(x,y0,z1)]);faces.append((i,i+1,i+2,i+3))
# The two paired east-wing windows are estimated photo-derived placements, not surveyed.
for cy in (-18.795,19.40):
    for z0,z1 in ((1.92,4.27),(6.62,8.27)):
        half=1.175; border=0.28; x=2.255
        # Brick side jambs and broad top/bottom inlay panels (flat mesh behind glazing).
        quad(x,cy-half-border,cy-half,z0-0.05,z1+0.05)
        quad(x,cy+half,cy+half+border,z0-0.05,z1+0.05)
        quad(x,cy-half-border,cy+half+border,z0-0.36,z0-0.05)
        quad(x,cy-half-border,cy+half+border,z1+0.05,z1+0.36)
# Corner inlay bands on the two outer edges of the long east elevation.
for cy0,cy1 in [(-26.0,-25.45),(26.05,26.6)]:quad(2.255,cy0,cy1,1.05,9.35)
mesh=bpy.data.meshes.new('HAAS_R8_EastWing_InlayMesh');mesh.from_pydata(verts,[],faces);mesh.materials.append(brick);mesh.update()
obj=bpy.data.objects.new('HAAS_R8_EastWing_Brick_Inlays_EST',mesh);C.objects.link(obj)
obj['evidence_basis']='Purdue exterior photograph shows red-brick surrounds/corner inlay within a pale limestone east facade. Exact wing extents are estimates; GIS footprint locates wall plane only.'
obj['estimated_openings']='Two east-wing upper/lower paired window locations follow current estimated window schedule; not verified by measured elevation.'
# Remove side-window assemblies that extend past the GIS north extent and form stray edge projections.
removed=[]
for name in ['HAAS_Estimated_Side_Upper_Glass_N_4_R4','HAAS_Estimated_Side_Lower_Glass_N_4_R4',
             'HAAS_Estimated_Side_Upper_Jamb_N_4_-1.27_R4','HAAS_Estimated_Side_Upper_Jamb_N_4_1.27_R4',
             'HAAS_Estimated_Side_Lower_Jamb_N_4_-1.27_R4','HAAS_Estimated_Side_Lower_Jamb_N_4_1.27_R4',
             'HAAS_Estimated_Side_Upper_Head_N_4_R4','HAAS_Estimated_Side_Upper_Sill_N_4_R4',
             'HAAS_Estimated_Side_Lower_Head_N_4_R4','HAAS_Estimated_Side_Lower_Sill_N_4_R4']:
    o=bpy.data.objects.get(name)
    if o:removed.append(name);bpy.data.objects.remove(o,do_unlink=True)
# Reduce roof color/shading extremes while retaining its tile texture and silhouette estimate.
roofmat=bpy.data.materials.get('HAAS_GooglePhotos_RedClayTiles_estimated')
if roofmat:
    roofmat.diffuse_color=(0.23,0.045,0.018,1)
    for node in roofmat.node_tree.nodes:
        if node.type=='TEX_BRICK':
            node.inputs['Color1'].default_value=(0.28,0.055,0.021,1)
            node.inputs['Color2'].default_value=(0.20,0.031,0.012,1)
            node.inputs['Mortar'].default_value=(0.14,0.025,0.010,1)
        if node.type=='BUMP':node.inputs['Strength'].default_value=min(node.inputs['Strength'].default_value,0.08)
        if node.type=='BSDF_PRINCIPLED':node.inputs['Roughness'].default_value=0.86
for o in C.objects:
    if o.name=='HAAS_Brick_Wall_East':o['round8_facade']='Purdue exterior photo guided a continuous warm limestone field on the east GIS envelope and central projection; exact upper facade extent is estimated.'
obj['round8_change']='Extended red brick surrounds and corner inlays onto the two flanking east wings; estimated and photo-based, not survey derived.'
Path('audit/batch3_haas/round8_changes.json').write_text(json.dumps({'east_wing_limestone_faces_reassigned':len(facade_faces),'new_east_wing_brick_inlay_faces':len(faces),'removed_end_glazing_objects':removed,'gis_bounds_vertices_moved':False,'estimated_inlay_geometry':True,'roof_material_tuned':bool(roofmat)},indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('ROUND8',len(facade_faces),len(faces),removed,len(C.objects))
