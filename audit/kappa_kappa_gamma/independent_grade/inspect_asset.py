import bpy, json, math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[3]
asset_id='massing_house_301840871_5d1bc06'
feature=json.loads((root/'audit/kappa_kappa_gamma/sources/purdue_gis_fid782_raw.json').read_text(encoding='utf-8-sig'))['features'][0]
ring=feature['geometry']['rings'][0]
if ring[0]==ring[-1]: ring=ring[:-1]
lat0,lon0=40.4274,-86.9137
expected=[Vector(((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0,0.0)) for lon,lat in ring]
coll=bpy.data.collections.get('Asset_'+asset_id)
assert coll is not None
objects=list(coll.objects)
assert len(objects)==1
obj=objects[0]
base=[v.co.copy() for v in obj.data.vertices if abs(v.co.z)<1e-6]
errs=[min((candidate-point).length for candidate in base) for point in expected]
bpy.context.view_layer.update()
world=[obj.matrix_world@Vector(corner) for corner in obj.bound_box]
result={'asset_id':asset_id,'collection':coll.name,'collection_object_count':len(objects),'object_name':obj.name,'object_type':obj.type,'identity_location_rotation':all(abs(v)<1e-6 for v in (*obj.location,*obj.rotation_euler)),'identity_scale':all(abs(v-1.0)<1e-6 for v in obj.scale),'source_fid':feature['attributes']['FID'],'gis_vertices':len(expected),'matched_vertices':sum(e<1e-4 for e in errs),'max_footprint_residual_m':max(errs),'bounds_world_m':{axis:[round(min(p[i] for p in world),6),round(max(p[i] for p in world),6)] for i,axis in enumerate('xyz')},'external_unpacked_images':[image.filepath for image in bpy.data.images if image.source=='FILE' and image.filepath and not image.packed_file],'modifier_count':len(obj.modifiers)}
print('GRADER_ASSET_JSON='+json.dumps(result,sort_keys=True))
