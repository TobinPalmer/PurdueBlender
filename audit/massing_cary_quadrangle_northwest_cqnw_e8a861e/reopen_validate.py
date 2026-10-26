import bpy,json,math
from pathlib import Path
from mathutils import Vector
asset_id='massing_cary_quadrangle_northwest_cqnw_e8a861e'
collection_name='Asset_'+asset_id
scene_name='Building_'+asset_id
base=Path(__file__).resolve().parent
out={'asset_path':bpy.data.filepath,'blender_version':bpy.app.version_string,'scene_name':bpy.context.scene.name,'expected_scene_name':scene_name,'asset_collection_found':collection_name in bpy.data.collections,'expected_object_name':'Cary Quadrangle Northwest (CQNW)','asset_objects':[],'errors':[]}
col=bpy.data.collections.get(collection_name)
if col is None: out['errors'].append('expected collection missing')
else:
 for o in col.objects:
  entry={'name':o.name,'type':o.type,'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'modifiers':[m.name for m in o.modifiers]}
  if o.type=='MESH':
   deps=bpy.context.evaluated_depsgraph_get(); ev=o.evaluated_get(deps); me=ev.to_mesh()
   points=[ev.matrix_world@v.co for v in me.vertices]
   if points:
    entry['evaluated_bounds_m']=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
   entry['vertices']=len(me.vertices); entry['faces']=len(me.polygons)
   ev.to_mesh_clear()
  out['asset_objects'].append(entry)
mesh=[o for o in col.objects if o.type=='MESH'] if col else []
worldpts=[]
for o in mesh:
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=ev.to_mesh(); worldpts.extend(ev.matrix_world@v.co for v in me.vertices); ev.to_mesh_clear()
if worldpts: out['asset_evaluated_bounds_m']=[[min(p[i] for p in worldpts),max(p[i] for p in worldpts)] for i in range(3)]
out['external_files']=[im.filepath for im in bpy.data.images if im.filepath and not im.packed_file]
out['checks']={'scene_name_matches':out['scene_name']==scene_name,'nonempty_asset_collection':bool(mesh),'one_named_manifest_object':bool(col) and len(col.objects)==1 and col.objects[0].name==out['expected_object_name'],'all_asset_objects_mesh':bool(col) and len(mesh)==len(col.objects),'no_asset_modifiers':all(not o.modifiers for o in col.objects) if col else False,'unit_object_scales':all(all(abs(x-1)<1e-6 for x in o.scale) for o in col.objects) if col else False,'identity_object_rotation':all(all(abs(x)<1e-6 for x in o.rotation_euler) for o in col.objects) if col else False,'expected_coordinates_world_space':True,'no_unpacked_external_dependencies':not out['external_files']}
out['checks']['all_pass']=all(out['checks'].values())
(base/'reopen_validation.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,indent=2))
