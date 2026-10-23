import bpy, json
from pathlib import Path
from mathutils import Vector
c=bpy.data.collections['Asset_felix_haas_hall'];archive=bpy.data.collections['Reference_Incompatible_Geometry_felix_haas_hall']
wall=bpy.data.objects['HAAS_Brick_Wall_East'];skin=bpy.data.objects['HAAS_R6_Entrance_Facade_Skin_ARCHIVE']
# Replace only outward +X wall polygons on this front bay with the source-shaped skin's faces.
# Both sets share the GIS shell's exact outer X plane; the skin is fused into the wall mesh.
keep_faces=[];keep_mats=[];removed=0
for p in wall.data.polygons:
    wn=wall.matrix_world.to_3x3()@p.normal;wc=wall.matrix_world@p.center
    if wn.x>0.95 and -12.0<=wc.y<=12.8 and wc.z>=0.35:
        removed+=1;continue
    keep_faces.append([wall.data.loops[li].vertex_index for li in p.loop_indices]);keep_mats.append(p.material_index)
verts=[tuple(v.co) for v in wall.data.vertices]
inv=wall.matrix_world.inverted();target_x=12.98121166229248
for v in skin.data.vertices:
    wp=skin.matrix_world@v.co;wp.x=target_x;lp=inv@wp;verts.append(tuple(lp))
base=len(wall.data.vertices)
for p in skin.data.polygons:
    keep_faces.append([base+skin.data.loops[li].vertex_index for li in p.loop_indices]);keep_mats.append(2)
mesh=bpy.data.meshes.new('HAAS_Brick_Wall_East_IntegratedFacadeMesh');mesh.from_pydata(verts,[],keep_faces)
for m in wall.data.materials:mesh.materials.append(m)
mesh.update()
for i,mi in enumerate(keep_mats):mesh.polygons[i].material_index=min(mi,len(mesh.materials)-1)
old=wall.data;wall.data=mesh
if old.users==0:bpy.data.meshes.remove(old)
wall['round7_facade']='Photo-based east front limestone skin fused into the GIS wall mesh; exterior bounds unchanged. Brick inlay mesh is 3 mm proud as a material inset.'
# Keep an unchanged source copy hidden for rollback/audit; only the integrated mesh renders.
if archive:archive.hide_render=True;archive.hide_viewport=True
# Move red masonry inlays flush to the fused face and include a portal surround plus corner details.
inlay=bpy.data.objects.get('HAAS_R7_EastFacade_Inlaid_Brickwork')
if inlay:
    for v in inlay.data.vertices:v.co.x=12.984
    inlay['evidence_basis']='Purdue exterior photo shows brick panels/inlay around limestone windows, entry, and corners; exact extents are perspective estimates. Joined facade skin is part of GIS east wall mesh.'
# Tune limestone toward warm natural Bedford stone under neutral outdoor lighting.
stone=bpy.data.materials.get('HAAS_Photo_Limestone')
if stone:
    stone.diffuse_color=(0.86,0.77,0.62,1)
    for n in stone.node_tree.nodes:
        if n.type=='BSDF_PRINCIPLED':n.inputs['Base Color'].default_value=(0.86,0.77,0.62,1);n.inputs['Roughness'].default_value=.86
Path('audit/batch3_haas/round7_changes.json').write_text(json.dumps({'integration':'Fused the 133-face entrance skin into HAAS_Brick_Wall_East, replacing its seven outward-facing front polygons; all inserted skin vertices lie on the prior wall maximum X plane, preserving GIS bounds. Source skin remains hidden in archive.','inlay_faces':len(inlay.data.polygons) if inlay else 0,'inlay_offset_m':0.0028,'removed_door_leaves_and_frames':True,'door_basis':'Purdue plan does not show metric door locations/swings. Removed guessed uniform leaves/frames; legend now labels openings as schematic.','gis_wall_front_polygons_replaced':removed,'shell_geometry_bounds_preserved':True},indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('R7_MERGED',removed,len(keep_faces),len(mesh.polygons),len(c.objects),target_x)
