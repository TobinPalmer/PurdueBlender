import bpy,json,math,os
from mathutils import Vector
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','..'))
AUDIT=os.path.join(ROOT,'audit','massing_johnson_hall_of_nursing_jnsn_823fca7')
SOURCE=os.path.join(AUDIT,'sources','purdue_building_shapes_fid218_jnsn.json')
OUT=os.path.join(AUDIT,'review','reopen_validation.json')
ID='massing_johnson_hall_of_nursing_jnsn_823fca7'
coll=bpy.data.collections.get('Asset_'+ID); scene=bpy.data.scenes.get('Building_'+ID)
assert coll and scene and scene.get('building_id')==ID and len(coll.objects)==1
obj=next(iter(coll.objects)); assert obj.type=='MESH'
deps=bpy.context.evaluated_depsgraph_get(); ev=obj.evaluated_get(deps); mesh=ev.to_mesh()
world=[ev.matrix_world@v.co for v in mesh.vertices]
bounds=[[min(v[k] for v in world),max(v[k] for v in world)] for k in range(3)]
base=[ev.matrix_world@v.co for v in mesh.vertices if abs((ev.matrix_world@v.co).z)<1e-5]
with open(SOURCE,encoding='utf-8-sig') as f: feature=json.load(f)['feature']
raw=feature['geometry']['rings'][0]
ring=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in raw]
if ring and math.dist(ring[0],ring[-1])<1e-8: ring=ring[:-1]
clean=[]
for p in ring:
 if not clean or math.dist(p,clean[-1])>.01: clean.append(p)
if len(clean)>2 and math.dist(clean[0],clean[-1])<=.01: clean.pop()
errors=[min(math.hypot(v.x-x,v.y-y) for v in base) for x,y in clean]
roof_height=obj.get('roof_height_m_lidar_median')
assert roof_height is not None and abs((bounds[2][1]-bounds[2][0])-roof_height)<.02
assert abs(obj.get('roof_height_m_lidar_interior_p95')-8.184)<.01
external=[{'path':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images if i.source=='FILE']
renders=[os.path.join(AUDIT,'renders','johnson_hall_nursing_exterior_preview.png'),os.path.join(AUDIT,'renders','johnson_hall_nursing_plan_preview.png'),os.path.join(AUDIT,'renders','johnson_hall_nursing_southwest_facade.png')]
assert len(clean)==12 and max(errors)<.001
assert len(obj.modifiers)==0 and not external and all(os.path.isfile(p) for p in renders)
assert any(m and 'brick (Purdue historic record)' in m.name for m in mesh.materials)
assert any(m and 'upper ribbon glazing (2007 panorama)' in m.name for m in mesh.materials)
assert not any(m and ('limestone' in m.name.lower() or 'entry' in m.name.lower()) for m in mesh.materials)
source_snapshot=os.path.join(AUDIT,'sources','purdue_historic_building_record_jnsn.html')
assert os.path.isfile(source_snapshot) and os.path.getsize(source_snapshot)>1000
result={'reopened_saved_asset':True,'asset':'modular/buildings/'+ID+'.blend','scene':scene.name,'scene_building_id':scene.get('building_id'),'collection':coll.name,'collection_object_count':len(coll.objects),'object':obj.name,'mesh_vertices':len(mesh.vertices),'mesh_faces':len(mesh.polygons),'modifiers':[m.name for m in obj.modifiers],'materials':[m.name if m else None for m in mesh.materials],'world_bounds_m':bounds,'dimensions_m':[q[1]-q[0] for q in bounds],'object_location':list(obj.location),'world_transform':[[float(obj.matrix_world[r][c]) for c in range(4)] for r in range(4)],'source':{'provider':'Purdue University BuildingShapesZip4 layer 0','FID':feature['attributes']['FID'],'name':feature['attributes']['BUILDING_N'],'code':feature['attributes']['BLDG_ABBR'],'raw_ring_vertices':len(raw),'clean_ring_vertices':len(clean),'source_vertices_nearest_mesh_ground_vertex_error_max_m':max(errors),'source_vertices_nearest_mesh_ground_vertex_error_mean_m':sum(errors)/len(errors),'comparison_transform':'X=(lon+86.9137)*111412.84*cos(radians(40.4274)); Y=(lat-40.4274)*111040.0','area_attribute_m2':feature['attributes'].get('Shape__Area'),'ring_area_m2_local_approx':984.0055712634894,'osm_way_117146488_ring_area_m2_local_approx':1005.8637256830366,'area_discrepancy':'Purdue Shape__Area attribute conflicts with source-ring geometry; OSM footprint corroborates the ring area and shape.'},'height':{'gis_num_levels':feature['attributes'].get('NUM_LEVELS'),'gis_extrution_raw':feature['attributes'].get('Extrution'),'height_estimate_m':bounds[2][1]-bounds[2][0],'floor_to_floor_derived_estimate_m':obj.get('floor_to_floor_m_derived_estimate'),'lidar_median_m':roof_height,'lidar_interior_p95_m':obj.get('roof_height_m_lidar_interior_p95'),'lidar_source':obj.get('roof_height_source'),'status':'main roof elevation measured from 2018 LiDAR surface returns; floor spacing is derived from roof height divided by GIS-reported levels; facade and parapet details remain unverified.'},'facade':{'verified_material':'brick per Purdue historic record','corroborating_image':'September 2007 Street View panorama A9uia6rcKZF_CDi5NSntjQ','modeled_feature':'single upper-story ribbon on southwest-facing GIS segment 0','render_bay_count_proxy':8,'entrance':'omitted; not supported by visible evidence','limestone_trim':'omitted; no support found'},'external_file_images':external,'renders':[os.path.relpath(p,ROOT).replace('\\','/') for p in renders]}
ev.to_mesh_clear()
with open(OUT,'w',encoding='utf-8') as f: json.dump(result,f,indent=2)
print('JNSN_REOPEN_VALIDATION',json.dumps(result))
