import bpy,json,math
from pathlib import Path
from mathutils import Vector
folder=Path(__file__).resolve().parent
cfg=json.loads((folder/'build_config.json').read_text(encoding='utf-8-sig'))
feature=json.loads((folder/cfg['source_feature_file']).read_text(encoding='utf-8-sig'))
attrs=feature['attributes']; raw=feature['geometry']['rings'][0]
if raw[0]==raw[-1]: raw=raw[:-1]
obj=bpy.data.objects.get(cfg['object_name']); coll=bpy.data.collections.get(cfg['collection_name'])
if obj is None or coll is None or obj not in coll.objects[:] or len(coll.objects)!=1: raise RuntimeError('Assigned asset collection mismatch')
def project(lon,lat): return ((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0,0.0)
source=[project(lon,lat) for lon,lat in raw]
world=obj.matrix_world
base=[world@v.co for v in obj.data.vertices if abs((world@v.co).z)<1e-5]
errors=[min(math.dist(p,tuple(q)) for q in base) for p in source]
if max(errors)>0.001: raise RuntimeError(f'Official source ring error {max(errors)} m')
verts=[world@v.co for v in obj.data.vertices]
lo=[min(v[i] for v in verts) for i in range(3)]; hi=[max(v[i] for v in verts) for i in range(3)]
result={'opened':True,'blender_version':bpy.app.version_string,'asset_id':cfg['asset_id'],'feature_id':attrs['FID'],'object':obj.name,'collection_objects':len(coll.objects),'source_ring_vertices':len(source),'max_source_ring_error_m':round(max(errors),8),'mesh_vertices':len(obj.data.vertices),'mesh_faces':len(obj.data.polygons),'modifiers':[m.name for m in obj.modifiers],'world_matrix':[[round(float(x),8) for x in row] for row in world],'bounds_world_m':[[round(lo[i],6),round(hi[i],6)] for i in range(3)],'materials':[m.name for m in obj.data.materials]}
(folder/'reopen_validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('REOPEN_VALIDATION='+json.dumps(result))
