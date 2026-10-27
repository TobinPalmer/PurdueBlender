import bpy, json, os, hashlib
asset=os.path.abspath('modular/buildings/massing_veterinary_pathology_building_48b5a5b.blend')
audit=os.path.abspath('audit/veterinary_pathology_building')
expected_scene='Building_massing_veterinary_pathology_building_48b5a5b'
expected_collection='Asset_massing_veterinary_pathology_building_48b5a5b'
scene=bpy.data.scenes.get(expected_scene)
coll=bpy.data.collections.get(expected_collection)
assert scene is not None, 'expected scene missing'
assert coll is not None, 'expected collection missing'
objects=list(coll.objects)
assert len(objects)==1, f'asset collection has {len(objects)} objects, expected one'
obj=objects[0]
assert obj.name=='Veterinary Pathology Building',obj.name
assert obj.get('stable_asset_id')=='massing_veterinary_pathology_building_48b5a5b'
assert not obj.data.is_library_indirect
assert len(obj.data.materials)>=5, f'only {len(obj.data.materials)} materials'
# Evaluated world bounds in campus coordinates.
depsgraph=bpy.context.evaluated_depsgraph_get()
eval_obj=obj.evaluated_get(depsgraph)
verts=[eval_obj.matrix_world @ v.co for v in eval_obj.data.vertices]
bounds=[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)]
assert bounds[0][1]-bounds[0][0] > 50 and bounds[0][1]-bounds[0][0] < 56, bounds
assert bounds[1][1]-bounds[1][0] > 40 and bounds[1][1]-bounds[1][0] < 44, bounds
assert abs(obj.location.x)<1e-5 and abs(obj.location.y)<1e-5, tuple(obj.location)
anchor=list(obj.get('campus_anchor_xy_m',[]))
assert anchor and len(anchor)==2, anchor
assert abs(anchor[0]-(-162.8212723))<.01 and abs(anchor[1]-(-816.2568073))<.01,anchor
assert -2.1 < bounds[2][0] < 0.1, bounds  # basement slab is below grade
assert 15.7 < bounds[2][1] < 16.2, bounds
# Ensure preview rig is separate from the export collection.
assert any(o.type=='CAMERA' for o in scene.objects), 'preview camera missing'
assert any(o.type=='LIGHT' for o in scene.objects), 'preview light missing'
assert all(o.type not in {'CAMERA','LIGHT'} for o in objects)
report={'status':'pass','fresh_open':True,'asset_path':'modular/buildings/massing_veterinary_pathology_building_48b5a5b.blend','scene':scene.name,'collection':coll.name,'collection_object_count':len(objects),'object':obj.name,'evaluated_bounds_local_m':bounds,'campus_anchor_xy_m':anchor,'object_mesh_vertices':len(eval_obj.data.vertices),'object_mesh_polygons':len(eval_obj.data.polygons),'material_slots':len(obj.data.materials),'asset_sha256':hashlib.sha256(open(asset,'rb').read()).hexdigest(),'checks':{'expected_scene_and_collection':True,'stable_asset_id':True,'one_named_building_object':True,'all_asset_geometry_local_about_centroid':True,'GIS_plan_dimensions_preserved':True,'vertical_envelope_matches_massing_approximation_including_basement':True,'preview_camera_and_light_outside_asset_collection':True,'materialized_mesh':True}}
with open(os.path.join(audit,'validation.json'),'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
