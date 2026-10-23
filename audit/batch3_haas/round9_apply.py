import bpy,json
from pathlib import Path
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall']
# Convert the east-facade brick strips into shallow solid masonry pieces with chamfered edges.
def make_relief(obj_name, back_x, bevel_width=0.012):
    obj=bpy.data.objects.get(obj_name)
    if not obj or obj.type!='MESH':return 0
    src=obj.data; newverts=[];newfaces=[];mats=[]
    for p in src.polygons:
        pts=[obj.matrix_world@src.vertices[src.loops[li].vertex_index].co for li in p.loop_indices]
        if len(pts)!=4:continue
        front=[Vector((q.x,q.y,q.z)) for q in pts]
        back=[Vector((back_x,q.y,q.z)) for q in pts]
        base=len(newverts);newverts.extend([tuple(q) for q in front+back])
        newfaces.append(tuple(base+i for i in (0,1,2,3)));mats.append(p.material_index)
        newfaces.append(tuple(base+i for i in (7,6,5,4)));mats.append(p.material_index)
        for i in range(4):newfaces.append((base+i,base+(i+1)%4,base+4+(i+1)%4,base+4+i));mats.append(p.material_index)
    mesh=bpy.data.meshes.new(obj_name+'_ReliefMesh');mesh.from_pydata(newverts,[],newfaces)
    for m in src.materials:mesh.materials.append(m)
    mesh.update()
    for i,mi in enumerate(mats):mesh.polygons[i].material_index=min(mi,len(mesh.materials)-1)
    old=src;obj.data=mesh;obj.location=(0,0,0);obj.rotation_euler=(0,0,0);obj.scale=(1,1,1)
    if old.users==0:bpy.data.meshes.remove(old)
    mod=obj.modifiers.new('Small stone-set edge chamfer','BEVEL');mod.width=bevel_width;mod.segments=1;mod.limit_method='ANGLE'
    obj['round9_relief']='Individual brick inlay pieces now have a solid return and small chamfer; GIS wall vertices/bounds unchanged.'
    return len(newfaces)
# The wall face is at the GIS maximum; relief backs extend into the wall, front remains within 3 mm of shell.
main_faces=make_relief('HAAS_R7_EastFacade_Inlaid_Brickwork',12.82,0.008)
wing_faces=make_relief('HAAS_R8_EastWing_Brick_Inlays_EST',2.10,0.015)
# Side glazing, frames and unsupported horizontal belt bands were estimated in a photo that does not show those elevations.
removed=[]
for o in list(C.objects):
    nm=o.name
    if (nm.startswith('HAAS_R5_Pavilion_South_A_') or nm.startswith('HAAS_R5_Pavilion_South_B_') or
        nm.startswith('HAAS_R5_Pavilion_North_A_') or nm.startswith('HAAS_R5_Pavilion_North_B_') or
        nm.startswith('HAAS_R5_Pavilion_SouthBand_') or nm.startswith('HAAS_R5_Pavilion_NorthBand_')):
        removed.append(nm);bpy.data.objects.remove(o,do_unlink=True)
# Keep vertical side piers; remove unsupported blue glazing and protruding horizontal bars only.
# Give all four roof facets the same material and soften bump; render with an overhead fill for even facet lighting.
roof=bpy.data.materials.get('HAAS_GooglePhotos_RedClayTiles_estimated')
if roof:
    for node in roof.node_tree.nodes:
        if node.type=='BUMP':node.inputs['Strength'].default_value=0.02
        if node.type=='BSDF_PRINCIPLED':node.inputs['Roughness'].default_value=0.94
# Mark the pavilion side schedule as intentionally removed pending a side-elevation source.
C['round9_side_evidence']='Removed the speculative north/south pavilion glass, surround frames, and belt bands. The Purdue photo does not resolve these side elevations; underlying GIS wall remains visible.'
C['round9_masonry']='Replaced flat front inlay cards with bevelled solid brick pieces; the GIS envelope mesh and coordinates remain unchanged.'
Path('audit/batch3_haas/round9_changes.json').write_text(json.dumps({'east_main_relief_faces':main_faces,'east_wing_relief_faces':wing_faces,'removed_unverified_side_detail_count':len(removed),'removed_side_detail_names':removed,'GIS_shell_vertices_moved':False,'roof_mesh_normals_changed':False,'roof_material_bump_reduced':True},indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('ROUND9',main_faces,wing_faces,len(removed),len(C.objects))
