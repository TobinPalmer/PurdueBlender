import bpy, json, math, datetime
from pathlib import Path
asset=r'modular/buildings/massing_house_301841248_fe939c7.blend'
audit=Path(r'audit/alpha_xi_delta_fid788')
out=audit/'fresh_open_validation.json'
with (audit/'source_fid788.json').open(encoding='utf-8-sig') as f: packet=json.load(f)
raw=packet['features'][0]['geometry']['rings'][0][:-1]
source=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in raw]
bpy.ops.wm.open_mainfile(filepath=asset)
scene=bpy.data.scenes.get('Building_massing_house_301841248_fe939c7')
coll=bpy.data.collections.get('Asset_massing_house_301841248_fe939c7')
house=bpy.data.objects.get('House_301841248')
assert scene and coll and house and house.type=='MESH'
root_vertices=[house.matrix_world@v.co for v in house.data.vertices]
assert len(source)==24 and len(root_vertices)>48
# Builder preserves the source-derived lower footprint as the first 24 stable-root vertices.
base=root_vertices[:24]
max_ring_error=max(min(math.hypot(v.x-x,v.y-y) for v in base) for x,y in source)
coords={k:{'min':min(v[i] for v in root_vertices),'max':max(v[i] for v in root_vertices)} for i,k in enumerate(('x','y','z'))}
image_textures=[n.image.filepath for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
asset_objects=list(coll.objects); scene_objects=list(scene.objects); cameras=[o.name for o in scene_objects if o.type=='CAMERA']; lights=[o.name for o in scene_objects if o.type=='LIGHT']
checks={
 'expected_scene_and_named_collection':scene.name=='Building_massing_house_301841248_fe939c7' and coll.name=='Asset_massing_house_301841248_fe939c7',
 'stable_root_object_present':house.name=='House_301841248',
 'one_object_manifest_contract':len(asset_objects)==1 and len(scene_objects)==1 and asset_objects[0]==house,
 'source_footprint_vertices_retained':len(source)==24 and max_ring_error<0.0001,
 'no_saved_preview_cameras_or_lights':not cameras and not lights,
 'no_external_image_texture_dependencies':not image_textures,
 'interior_schematic_tag_present':'schematic' in house.get('interior_representation','').lower(),
 'roof_gap_closure_tag_present':'continuous roof' in house.get('roof_transition','').lower()
}
summary={
 'validated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'blender_version':bpy.app.version_string,
 'fresh_open':'PASS' if all(checks.values()) else 'FAIL','asset_path':asset,'asset_collection':coll.name,'scene_name':scene.name,
 'stable_root_object':house.name,'stable_root_mesh_vertices':len(house.data.vertices),'stable_root_mesh_faces':len(house.data.polygons),
 'asset_collection_object_count':len(asset_objects),'scene_object_count':len(scene_objects),'stable_root_bounds_world_m':{k:{q:round(v,4) for q,v in val.items()} for k,val in coords.items()},
 'source_footprint_unique_vertices':len(source),'max_source_to_root_vertex_error_m':max_ring_error,
 'saved_cameras':cameras,'saved_lights':lights,'external_image_dependencies':image_textures,
 'root_materials':[m.name for m in house.data.materials],'root_custom_properties':{k:house.get(k) for k in ('building_id','asset_contract','interior_representation','roof_transition')},
 'cutaway_preview':'audit/alpha_xi_delta_fid788/interior_cutaway_preview.png; rendered from the same geometry before joining components into the manifest-counted root mesh',
 'checks':checks
}
out.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2,ensure_ascii=False))
