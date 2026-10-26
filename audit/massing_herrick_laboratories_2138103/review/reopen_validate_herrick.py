import bpy, json, math, os
from mathutils import Vector

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','..'))
AUDIT=os.path.join(ROOT,'audit','massing_herrick_laboratories_2138103')
SOURCE=os.path.join(AUDIT,'sources','purdue_building_shapes_fid246_herl_2026-10-26.json')
OUT=os.path.join(AUDIT,'review','reopen_validation.json')
ASSET='modular/buildings/massing_herrick_laboratories_2138103.blend'
ID='massing_herrick_laboratories_2138103'
coll=bpy.data.collections.get('Asset_'+ID)
scene=bpy.data.scenes.get('Building_'+ID)
assert coll is not None and scene is not None
assert scene.get('building_id') in (None,ID)
mesh_objects=[o for o in coll.objects if o.type=='MESH']
assert len(coll.objects)==1 and len(mesh_objects)==1
obj=mesh_objects[0]
deps=bpy.context.evaluated_depsgraph_get(); ev=obj.evaluated_get(deps); mesh=ev.to_mesh()
world=[ev.matrix_world @ v.co for v in mesh.vertices]
world_bounds=[[min(v[k] for v in world),max(v[k] for v in world)] for k in range(3)]
vertex_count=len(mesh.vertices); face_count=len(mesh.polygons); ev.to_mesh_clear()
assert len(obj.modifiers)==0
with open(SOURCE,encoding='utf-8-sig') as f: feature=json.load(f)['features'][0]
assert feature['attributes']['FID']==246 and feature['attributes']['BLDG_ABBR']=='HERL' and feature['attributes']['BUILDING_N']=='Herrick Acoustics'
raw=feature['geometry']['rings'][0]
source=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in raw]
if source and math.dist(source[0],source[-1])<1e-8: source=source[:-1]
clean=[]
for p in source:
    if not clean or math.dist(p,clean[-1])>.01: clean.append(p)
if len(clean)>2 and math.dist(clean[0],clean[-1])<=.01: clean.pop()
base=[ev.matrix_world @ v.co for v in obj.data.vertices if abs((ev.matrix_world @ v.co).z)<1e-5]
errors=[min(math.hypot(v.x-p[0],v.y-p[1]) for v in base) for p in clean]
max_error=max(errors); mean_error=sum(errors)/len(errors)
external=[]
for image in bpy.data.images:
    if image.source=='FILE' and image.filepath and not image.packed_file:
        external.append({'path':image.filepath,'resolved_exists':os.path.exists(bpy.path.abspath(image.filepath))})
render_paths=[os.path.join(AUDIT,'renders','herrick_acoustics_courtyard_preview.png'),os.path.join(AUDIT,'renders','herrick_acoustics_plan_preview.png')]
assert all(os.path.exists(p) for p in render_paths)
assert abs(world_bounds[2][0])<1e-4 and 10.8<=world_bounds[2][1]<=11.2
assert max_error<.001
result={
 'saved_and_reopened':True,'asset':ASSET,'scene':scene.name,'collection':coll.name,'object':obj.name,
 'collection_object_count':len(coll.objects),'mesh_object_count':len(mesh_objects),'modifier_count':len(obj.modifiers),
 'mesh_vertex_count':vertex_count,'mesh_face_count':face_count,
 'bounds_m':{'x':world_bounds[0],'y':world_bounds[1],'z':world_bounds[2]},
 'dimensions_m':[world_bounds[k][1]-world_bounds[k][0] for k in range(3)],
 'source':{'provider':'Purdue University BuildingShapesZip4 layer 0','feature_id':246,'code':'HERL','name':'Herrick Acoustics','crs':'EPSG:4326 response transformed to the project approximate local campus frame','converted_ring_vertex_count':len(clean),'footprint_vertex_nearest_error_max_m':max_error,'footprint_vertex_nearest_error_mean_m':mean_error,'source_shape_area_attribute_m2':feature['attributes'].get('Shape__Area'),'converted_ring_shoelace_area_m2':abs(sum(clean[i][0]*clean[(i+1)%len(clean)][1]-clean[(i+1)%len(clean)][0]*clean[i][1] for i in range(len(clean)))/2),'area_field_discrepancy_note':'GIS Shape__Area attribute does not match area recomputed from the returned ring using project transform; geometry ring is used for the shell, area field is not used.'},
 'height':{'nominal_gis_extrution_field':feature['attributes'].get('Extrution'),'interpreted_as':'feet','max_height_m':world_bounds[2][1],'wing_height_m_estimate':5.2,'uncertainty':'GIS metadata omits Extrution units; model height is an estimate.'},
 'external_images':external,'renders':[os.path.relpath(p,ROOT).replace('\\','/') for p in render_paths],
 'before_bounds_m':{'x':[-633.1705322265625,-596.0997924804688],'y':[-536.5675048828125,-482.7908020019531],'z':[0.0,16.0]},
 'edits':['Replaced fallback shell polygon with Purdue GIS FID 246 HERL ring after approximate campus transform.','Rebuilt low wings and central raised barn from GIS outline plus historic source photos.','Added gabled roof, cupola, dormers, brick/window rhythm, and approximate courtyard entrance.'],
 'unresolved':['The GIS structural polygon is not a surveyed wall footprint.','GIS Extrution=36 unit interpretation as feet is unconfirmed; 3-floor attribute conflicts with varying wing heights in photos.','Low wing height, barn core subdivisions, facade/window stations, roof details, and entry exact location are estimated.','GIS Shape__Area field (5174.79) conflicts with transformed ring area (~2993.81 m2); geometry ring used, area attribute not used.']
}
with open(OUT,'w',encoding='utf-8') as f: json.dump(result,f,indent=2)
print('HERRICK_REOPEN_VALIDATION',json.dumps(result))

