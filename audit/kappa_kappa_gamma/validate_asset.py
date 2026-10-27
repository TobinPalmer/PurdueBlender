import json, math, os
from pathlib import Path
import bpy
from mathutils import Vector
asset_id='massing_house_301840871_5d1bc06'
audit=Path(__file__).resolve().parent
collection=bpy.data.collections.get('Asset_'+asset_id)
assert collection and len(collection.objects)==1
obj=collection.objects[0]
assert obj.type=='MESH'
feature=json.loads((audit/'sources'/'purdue_gis_fid782_raw.json').read_text(encoding='utf-8-sig'))['features'][0]
assert feature['attributes']['FID']==782 and feature['attributes']['BLDG_ABBR']=='SOKKG'
ring=feature['geometry']['rings'][0]
if ring[0]==ring[-1]: ring=ring[:-1]
lat0,lon0=40.4274,-86.9137
expected=[Vector(((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.,0)) for lon,lat in ring]
base=[v.co.copy() for v in obj.data.vertices if abs(v.co.z)<1e-6]
errors=[min((candidate-p).length for candidate in base) for p in expected]
max_error=max(errors)
assert max_error<1e-4, f'GIS boundary mismatch: {max_error}'
assert all(abs(v)<1e-6 for v in (*obj.location,*obj.rotation_euler)) and all(abs(v-1)<1e-6 for v in obj.scale)
bpy.context.view_layer.update()
world=[obj.matrix_world@Vector(c) for c in obj.bound_box]
result={'asset_id':asset_id,'blend_file':bpy.data.filepath,'reopened_in_background_blender':True,'collection':collection.name,'collection_object_count':len(collection.objects),'object_name':obj.name,'object_type':obj.type,'identity_object_transform':True,'source_fid':782,'source_ring_vertices':len(expected),'matched_source_ring_vertices':len(expected),'max_source_ring_error_m':round(max_error,9),'mesh_vertices':len(obj.data.vertices),'mesh_faces':len(obj.data.polygons),'bounds_world_m':{axis:[round(min(p[i] for p in world),6),round(max(p[i] for p in world),6)] for i,axis in enumerate('xyz')},'external_unpacked_images':[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file],'passed':bool(obj.data.vertices and obj.data.polygons and not [i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file])}
(audit/'reopen_validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('REOPEN_VALIDATION_JSON='+json.dumps(result,sort_keys=True))
assert result['passed'], 'Asset validation failed or contains external unpacked images'
