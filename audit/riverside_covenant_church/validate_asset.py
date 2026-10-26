import bpy, json, math, os
from pathlib import Path
from mathutils import Vector
folder=Path(__file__).resolve().parent
asset_id='massing_riverside_covenannt_church_3a60684'
obj=bpy.data.objects.get('Riverside Covenannt Church')
collection=bpy.data.collections.get('Asset_'+asset_id)
if obj is None or collection is None or obj not in collection.objects[:] or len(collection.objects)!=1:
 raise RuntimeError('Assigned asset/collection structure is invalid')
feat=json.loads((folder/'indiana_building_footprint_feature_409445.json').read_text(encoding='utf-8-sig'))['features'][0]
def proj(lon,lat): return ((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0,0.0)
source=[proj(lon,lat) for lon,lat in feat['geometry']['rings'][0][:-1]]
world=obj.matrix_world
base=[world@v.co for v in obj.data.vertices if abs((world@v.co).z)<1e-5]
errors=[min(math.dist(p,tuple(q)) for q in base) for p in source]
if max(errors)>0.001: raise RuntimeError('Official GIS footprint vertex error %.6f m'%max(errors))
coords=[world@v.co for v in obj.data.vertices]
result={'opened':True,'blender_version':bpy.app.version_string,'asset_id':asset_id,'object':obj.name,'collection_objects':len(collection.objects),'official_source_feature_id':feat['attributes']['objectid'],'source_ring_vertices':len(source),'max_source_ring_error_m':round(max(errors),8),'mesh_vertices':len(obj.data.vertices),'mesh_faces':len(obj.data.polygons),'modifiers':[m.name for m in obj.modifiers],'bounds_world_m':[[round(min(v[i] for v in coords),6),round(max(v[i] for v in coords),6)] for i in range(3)],'materials':[m.name for m in obj.data.materials],'world_matrix':[[round(float(x),8) for x in row] for row in world]}
(folder/'reopen_validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('REOPEN_VALIDATION_JSON='+json.dumps(result))
