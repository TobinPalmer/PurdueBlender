"""Reopen-time checks for Meredith Hall's saved library. Run via Blender background."""
import json,math
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'meredith_hall'
raw=json.loads((AUDIT/'sources'/'feature_253_wgs84.geojson').read_text(encoding='utf-8'))
f=raw['features'][0]; ring=f['geometry']['coordinates'][0]
if ring[0]==ring[-1]: ring=ring[:-1]
expected=[((float(lon)+86.9137)*111412.84*math.cos(math.radians(40.4274)),(float(lat)-40.4274)*111040.0) for lon,lat in ring]
expected_edges=[(expected[i],expected[(i+1)%len(expected)]) for i in range(len(expected))]
obj=bpy.data.objects['Meredith Hall']
coll=bpy.data.collections['Asset_massing_meredith_hall_4bb4188']
world=[obj.matrix_world@v.co for v in obj.data.vertices]
actual_edges=[]
for poly in obj.data.polygons:
 pts=[obj.matrix_world@obj.data.vertices[i].co for i in poly.vertices]
 base=[(float(p.x),float(p.y)) for p in pts if abs(p.z)<1e-5]
 if len(base)==2: actual_edges.append(base)
def dist(a,b): return math.dist(a,b)
def edge_error(a,b):
 return min(max(dist(a[0],b[0]),dist(a[1],b[1])),max(dist(a[0],b[1]),dist(a[1],b[0])))
errs=[min((edge_error(e,a) for a in actual_edges),default=float('inf')) for e in expected_edges]
lo=[min(p[i] for p in world) for i in range(3)]; hi=[max(p[i] for p in world) for i in range(3)]
result={'saved_asset_reopened':bool(bpy.data.filepath),'asset_path':bpy.data.filepath,'asset_id':'massing_meredith_hall_4bb4188','object_name':obj.name,'object_type':obj.type,'export_collection':coll.name,'collection_object_count':len(coll.objects),'mesh_vertices':len(obj.data.vertices),'mesh_faces':len(obj.data.polygons),'materials':[m.name for m in obj.data.materials],'modifiers':[m.name for m in obj.modifiers],'source_ring_vertices':len(expected),'source_wall_edges_matched':sum(e<.002 for e in errs),'source_wall_edge_max_error_m':max(errs),'source_footprint_bounds_xy_m':{'min':[min(p[0] for p in expected),min(p[1] for p in expected)],'max':[max(p[0] for p in expected),max(p[1] for p in expected)]},'model_bounds_xyz_m':{'min':lo,'max':hi},'identity_transform':list(obj.location)==[0.0,0.0,0.0] and list(obj.rotation_euler)==[0.0,0.0,0.0] and list(obj.scale)==[1.0,1.0,1.0],'external_file_images':[im.filepath for im in bpy.data.images if im.source=='FILE']}
(AUDIT/'reopen_check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('MEREDITH_REOPEN='+json.dumps(result))
