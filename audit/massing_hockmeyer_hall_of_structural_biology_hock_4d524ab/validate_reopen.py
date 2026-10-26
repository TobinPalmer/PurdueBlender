import bpy, json, math, hashlib, os
ASSET='modular/buildings/massing_hockmeyer_hall_of_structural_biology_hock_4d524ab.blend'
AUDIT='audit/massing_hockmeyer_hall_of_structural_biology_hock_4d524ab'
SOURCE=os.path.join(AUDIT,'sources','purdue_building_shapes_hock.json')
EXPECTED_ID='massing_hockmeyer_hall_of_structural_biology_hock_4d524ab'
EXPECTED_SCENE='Building_'+EXPECTED_ID
EXPECTED_COLL='Asset_'+EXPECTED_ID
EXPECTED_OBJ='Hockmeyer Hall of Structural Biology (HOCK)'
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(ASSET))
scenes=list(bpy.data.scenes)
scene=bpy.context.scene
coll=bpy.data.collections.get(EXPECTED_COLL)
assert coll is not None, 'Expected asset collection missing'
assert len(coll.objects)==6, f'Expected 6 exported objects, got {len(coll.objects)}'
assert any(o.name==EXPECTED_OBJ for o in coll.objects), 'Main shell object missing'
assert scene.get('building_id')==EXPECTED_ID
with open(SOURCE,encoding='utf-8-sig') as f: feature=json.load(f)['features'][0]
raw=feature['geometry']['rings'][0]
ring=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in raw]
if ring and math.dist(ring[0],ring[-1])<1e-8:ring.pop()
if sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))*.5<0:ring.reverse()
shell=bpy.data.objects[EXPECTED_OBJ]
verts=[v.co for v in shell.data.vertices]
low=[v for v in verts if abs(v.z)<1e-6]
high=[v for v in verts if v.z>1e-6]
assert len(low)==len(ring) and len(high)==len(ring), f'Unexpected shell vertices: low={len(low)} high={len(high)} expected={len(ring)} each'
max_xy=max(min(math.hypot(v.x-x,v.y-y) for v in low) for x,y in ring)
xs=[v.x for v in low]; ys=[v.y for v in low]
images=[]
for name in ('hockmeyer_exterior_oblique.png','hockmeyer_courtyard_entry.png','hockmeyer_roof_plan.png'):
 p=os.path.join(AUDIT,'renders',name); assert os.path.getsize(p)>10000, f'Missing/empty render {name}'; images.append({'path':p.replace('\\','/'),'bytes':os.path.getsize(p)})
external=[]
for image in bpy.data.images:
 if image.source=='FILE' and image.filepath and not image.packed_file: external.append(image.filepath)
original=os.path.join(AUDIT,'original_asset_blender_5_2.blend')
original_hash=hashlib.sha256(open(original,'rb').read()).hexdigest() if os.path.exists(original) else None
result={
 'asset':ASSET,'opened_file':os.path.abspath(ASSET),'reopened':True,'blender_version':bpy.app.version_string,
 'expected_scene_name':EXPECTED_SCENE,'actual_scene_name':scene.name,'scene_name_matches':scene.name==EXPECTED_SCENE,
 'expected_scene_name_custom_property':scene.get('expected_scene_name'),'scene_name_custom_property_matches':scene.get('expected_scene_name')==EXPECTED_SCENE,
 'scene_name_note':'Blender 4.5.15 truncates the long required scene ID; this is a compatibility failure, not a pass.' if scene.name!=EXPECTED_SCENE else None,
 'expected_collection':EXPECTED_COLL,'collection_found':True,'collection_object_count':len(coll.objects),'main_shell_found':True,
 'collection_object_names':[o.name for o in coll.objects],
 'main_shell_height_estimate_m':round(max(v.z for v in verts)-min(v.z for v in verts),6),
 'separate_rooftop_penthouse_block_modeled':any('penthouse' in o.name.lower() for o in coll.objects),
 'source_fid':feature['attributes'].get('FID'),'ring_vertices_source':len(ring),'ring_vertices_shell_lower':len(low),'ring_vertices_shell_upper':len(high),'max_source_to_shell_xy_vertex_error_m':round(max_xy,9),
 'bounds_xy_m':[[round(min(xs),6),round(max(xs),6)],[round(min(ys),6),round(max(ys),6)]],
 'external_unpacked_file_dependencies':external,'renders':images,'original_5_2_backup_sha256':original_hash,
 'asset_id_custom_property':scene.get('building_id'),'passed_geometry_and_collection_checks':True,
 'passed_expected_scene_contract':scene.name==EXPECTED_SCENE
}
out=os.path.join(AUDIT,'reopen_validation.json')
with open(out,'w',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
