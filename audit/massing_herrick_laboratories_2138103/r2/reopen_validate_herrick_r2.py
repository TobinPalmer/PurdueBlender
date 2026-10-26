import bpy, json, math, os
from mathutils import Vector
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','..'))
AUDIT=os.path.join(ROOT,'audit','massing_herrick_laboratories_2138103')
R2=os.path.join(AUDIT,'r2')
SOURCE=os.path.join(AUDIT,'sources','purdue_building_shapes_fid246_herl_2026-10-26.json')
OUT=os.path.join(R2,'reopen_validation_r2.json')
ID='massing_herrick_laboratories_2138103'
coll=bpy.data.collections.get('Asset_'+ID); scene=bpy.data.scenes.get('Building_'+ID)
assert coll and scene and len(coll.objects)==1
obj=next(iter(coll.objects)); assert obj.type=='MESH'
deps=bpy.context.evaluated_depsgraph_get(); ev=obj.evaluated_get(deps); mesh=ev.to_mesh()
world=[ev.matrix_world @ v.co for v in mesh.vertices]
bounds=[[min(v[k] for v in world),max(v[k] for v in world)] for k in range(3)]
base=[ev.matrix_world @ v.co for v in mesh.vertices if abs((ev.matrix_world @ v.co).z)<1e-5]
with open(SOURCE,encoding='utf-8-sig') as f: feature=json.load(f)['features'][0]
raw=feature['geometry']['rings'][0]
ring=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in raw]
if ring and math.dist(ring[0],ring[-1])<1e-8: ring=ring[:-1]
clean=[]
for p in ring:
 if not clean or math.dist(p,clean[-1])>.01: clean.append(p)
if len(clean)>2 and math.dist(clean[0],clean[-1])<=.01: clean.pop()
errors=[min(math.hypot(v.x-x,v.y-y) for v in base) for x,y in clean]
ring_area=abs(sum(clean[i][0]*clean[(i+1)%len(clean)][1]-clean[(i+1)%len(clean)][0]*clean[i][1] for i in range(len(clean)))/2)
images=[{'filepath':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images if i.source=='FILE']
renders=[os.path.join(R2,'herrick_acoustics_courtyard_preview_r2.png'),os.path.join(R2,'herrick_acoustics_plan_preview_r2.png')]
assert len(clean)==66 and max(errors)<.001
assert all(os.path.isfile(p) for p in renders)
assert len(obj.modifiers)==0 and not images
result={
 'reopened_saved_asset':True,'asset':'modular/buildings/'+ID+'.blend','scene':scene.name,'collection':coll.name,
 'collection_object_count':len(coll.objects),'object':obj.name,'mesh_vertices':len(mesh.vertices),'mesh_faces':len(mesh.polygons),
 'modifiers':[m.name for m in obj.modifiers],'materials':[m.name if m else None for m in mesh.materials],
 'bounds_m':{'x':bounds[0],'y':bounds[1],'z':bounds[2]},'dimensions_m':[v[1]-v[0] for v in bounds],
 'source':{'provider':'Purdue University BuildingShapesZip4 layer 0','FID':feature['attributes'].get('FID'),'BLDG_ABBR':feature['attributes'].get('BLDG_ABBR'),'BUILDING_N':feature['attributes'].get('BUILDING_N'),'source_vertices_cleaned':len(clean),'base_vertices_at_ground':len(base),'nearest_base_vertex_error_max_m':max(errors),'nearest_base_vertex_error_mean_m':sum(errors)/len(errors),'ring_area_local_approx_m2':ring_area,'Shape__Area_attribute':feature['attributes'].get('Shape__Area'),'Shape__Area_to_ring_area_ratio':feature['attributes'].get('Shape__Area')/ring_area,'rings_in_source_polygon':len(feature['geometry']['rings']),'area_discrepancy':'Unresolved in service response; valid one-ring geometry is retained without area scaling.'},
 'height_estimates':{'wing_height_m':5.0,'barn_eave_m':6.9,'roof_ridge_m':9.25,'cupola_top_m':10.95,'GIS_Extrution_raw':feature['attributes'].get('Extrution'),'interpretation':'36 may be feet, but units are undocumented; total height is estimated, not measured.'},
 'external_file_images':images,'renders':[os.path.relpath(p,ROOT).replace('\\','/') for p in renders]
}
ev.to_mesh_clear()
with open(OUT,'w',encoding='utf-8') as f: json.dump(result,f,indent=2)
print('HERRICK_REOPEN_R2',json.dumps(result))

