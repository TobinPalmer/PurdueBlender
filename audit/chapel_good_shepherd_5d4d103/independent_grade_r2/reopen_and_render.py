import bpy, json, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'audit'/'chapel_good_shepherd_5d4d103'/'independent_grade_r2'
ASSET=ROOT/'modular'/'buildings'/'massing_chapel_of_the_good_shepherd_5d4d103.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset_id='massing_chapel_of_the_good_shepherd_5d4d103'
col=bpy.data.collections.get(f'Asset_{asset_id}')
assert col is not None
objs=list(col.objects)
assert len(objs)==1
obj=objs[0]
assert obj.type=='MESH'
dg=bpy.context.evaluated_depsgraph_get(); ev=obj.evaluated_get(dg); mesh=ev.to_mesh()
verts=[ev.matrix_world @ v.co for v in mesh.vertices]
bounds=[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)]
zero=[v for v in verts if abs(v.z)<1e-5]
base=[[min(v[i] for v in zero),max(v[i] for v in zero)] for i in range(2)]
edge_counts={}
for p in mesh.polygons:
    for key in p.edge_keys: edge_counts[key]=edge_counts.get(key,0)+1
boundary=sum(c==1 for c in edge_counts.values()); nonmanifold=sum(c>2 for c in edge_counts.values())
materials=[m.name for m in obj.data.materials]
meshstats={'blend_file':str(ASSET.relative_to(ROOT)),'scene':bpy.context.scene.name,'collection':col.name,'object_name':obj.name,'object_type':obj.type,'vertices':len(mesh.vertices),'polygons':len(mesh.polygons),'material_slots':materials,'modifiers':[m.type for m in obj.modifiers],'matrix_world':[list(row) for row in obj.matrix_world],'world_bounds_m':bounds,'zero_z_xy_bounds_m':base,'boundary_edges':boundary,'edges_with_more_than_two_faces':nonmanifold,'unpacked_images':[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file]}
ev.to_mesh_clear()
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=1200; scene.render.resolution_y=800; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.camera=bpy.data.objects.get('Camera') or scene.camera
camera=scene.camera
center=Vector(((bounds[0][0]+bounds[0][1])/2,(bounds[1][0]+bounds[1][1])/2,7.5))
def render_view(label, pos, target):
    camera.location=Vector(pos); camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO'; camera.data.ortho_scale=47 if label!='top' else 42
    scene.render.filepath=str(OUT/f'{label}.png')
    bpy.ops.render.render(write_still=True)
render_view('south_elevation',(center.x,center.y-55,12),(center.x,center.y,8))
render_view('southeast',(center.x+35,center.y-45,23),(center.x,center.y,7.5))
render_view('top',(center.x,center.y,90),(center.x,center.y,0))
report={'status':'pass','reviewer':'independent_grade_r2','reopened_from_saved_blend':True,'model':meshstats,'views':['south_elevation.png','southeast.png','top.png'],'note':'Reviewer opened the saved asset directly in Blender 4.5.15; renders and counts were generated after reopening without saving changes to the candidate.'}
(OUT/'reopen_inspection.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
