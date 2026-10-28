import bpy, json, os, math, hashlib, datetime
from pathlib import Path
asset=r'modular/buildings/massing_house_301841248_fe939c7.blend'
out=Path(r'audit/alpha_xi_delta_fid788/fresh_open_validation.json')
bpy.ops.wm.open_mainfile(filepath=asset)
scene=bpy.data.scenes.get('Building_massing_house_301841248_fe939c7')
coll=bpy.data.collections.get('Asset_massing_house_301841248_fe939c7')
house=bpy.data.objects.get('House_301841248')
assert scene and coll and house and house.type=='MESH'
assert len(house.data.vertices)==32
verts=[house.matrix_world @ v.co for v in house.data.vertices]
xyz={k:{'min':min(v[i] for v in verts),'max':max(v[i] for v in verts)} for i,k in enumerate(('x','y','z'))}
image_textures=[n.image.filepath for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
root_objects=list(coll.objects)
mesh_count=sum(o.type=='MESH' for o in root_objects)
scene_objs=list(scene.objects)
summary={
 'validated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'blender_version':bpy.app.version_string,
 'fresh_open':'PASS',
 'asset_path':asset,
 'scene_name':scene.name,
 'asset_collection':coll.name,
 'stable_root_object':house.name,
 'stable_root_object_mesh_vertices':len(house.data.vertices),
 'stable_root_object_bounds_world_m':{k:{q:round(v,4) for q,v in vals.items()} for k,vals in xyz.items()},
 'asset_collection_object_count':len(root_objects),
 'asset_collection_mesh_count':mesh_count,
 'scene_object_count':len(scene_objs),
 'mesh_material_image_dependencies':image_textures,
 'checks':{
  'expected_scene_and_collection':True,
  'stable_root_mesh_present':True,
  'all_asset_objects_linked_to_named_collection':all(coll in o.users_collection for o in root_objects),
  'no_external_image_texture_dependencies':not image_textures,
  'source_external_object_absent_from_asset_collection':not any(o.name in {'PreviewGround','AXiD_PreviewCamera','Key','Fill','Rim'} for o in root_objects)
 }
}
summary['fresh_open']='PASS' if all(summary['checks'].values()) else 'FAIL'
out.write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
