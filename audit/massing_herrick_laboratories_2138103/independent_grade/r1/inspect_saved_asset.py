import bpy, json, math, os
from mathutils import Vector
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','..','..'))
AUDIT=os.path.join(ROOT,'audit','massing_herrick_laboratories_2138103')
ASSET='modular/buildings/massing_herrick_laboratories_2138103.blend'
ID='massing_herrick_laboratories_2138103'
SOURCE=os.path.join(AUDIT,'sources','purdue_building_shapes_fid246_herl_2026-10-26.json')
OUT=os.path.join(os.path.dirname(__file__),'direct_inspection.json')
coll=bpy.data.collections.get('Asset_'+ID)
scene=bpy.data.scenes.get('Building_'+ID)
assert coll and scene
objs=list(coll.objects)
assert len(objs)==1 and objs[0].type=='MESH'
obj=objs[0]
deps=bpy.context.evaluated_depsgraph_get(); ev=obj.evaluated_get(deps); mesh=ev.to_mesh()
world=[ev.matrix_world @ v.co for v in mesh.vertices]
bounds=[[min(v[k] for v in world),max(v[k] for v in world)] for k in range(3)]
base=[(ev.matrix_world @ v.co) for v in mesh.vertices if abs((ev.matrix_world @ v.co).z)<1e-5]
with open(SOURCE,encoding='utf-8-sig') as f: feature=json.load(f)['features'][0]
raw=feature['geometry']['rings'][0]
source=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in raw]
if source and math.dist(source[0],source[-1])<1e-8: source=source[:-1]
clean=[]
for p in source:
 if not clean or math.dist(p,clean[-1])>.01: clean.append(p)
if len(clean)>2 and math.dist(clean[0],clean[-1])<=.01: clean.pop()
errors=[min(math.hypot(v.x-x,v.y-y) for v in base) for x,y in clean]
areas=lambda ps: abs(sum(ps[i][0]*ps[(i+1)%len(ps)][1]-ps[(i+1)%len(ps)][0]*ps[i][1] for i in range(len(ps)))/2)
materials=[m.name if m else None for m in obj.data.materials]
external=[{'path':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images if i.source=='FILE']
result={'asset':ASSET,'scene':scene.name,'scene_building_id':scene.get('building_id'),'collection':coll.name,'collection_object_count':len(objs),'object':obj.name,'object_type':obj.type,'modifiers':[m.name for m in obj.modifiers],'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'materials':materials,'bounds_m':bounds,'dimensions_m':[b[1]-b[0] for b in bounds],'base_vertex_count':len(base),'source':{'FID':feature['attributes'].get('FID'),'name':feature['attributes'].get('BUILDING_N'),'abbr':feature['attributes'].get('BLDG_ABBR'),'num_levels':feature['attributes'].get('NUM_LEVELS'),'extrution':feature['attributes'].get('Extrution'),'shape_area_attribute':feature['attributes'].get('Shape__Area'),'source_ring_vertices_after_cleaning':len(clean),'ring_shoelace_area_m2':areas(clean),'vertex_nearest_error_max_m':max(errors),'vertex_nearest_error_mean_m':sum(errors)/len(errors)},'external_file_images':external,'world_translation':list(obj.matrix_world.translation),'object_location':list(obj.location),'is_linked':obj.library is not None}
ev.to_mesh_clear()
with open(OUT,'w',encoding='utf-8') as f: json.dump(result,f,indent=2)
print(json.dumps(result))
