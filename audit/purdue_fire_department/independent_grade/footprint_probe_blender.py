import bpy, json, math, os, hashlib
from mathutils import Vector
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','..'))
asset_id='massing_purdue_fire_department_520430b'
blend=os.path.join(ROOT,'modular','buildings',asset_id+'.blend')
gis=os.path.join(ROOT,'audit','purdue_fire_department','sources','dmnt_feature_211.geojson')
bpy.ops.wm.open_mainfile(filepath=blend)
with open(gis,encoding='utf-8') as f: gj=json.load(f)
coords=gj['features'][0]['geometry']['coordinates'][0][:-1]
lat0,lon0=40.4274,-86.9137
source=[((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0) for lon,lat in coords]
obj=bpy.data.objects.get('DMNT | GIS-footprint brick station shell')
assert obj and obj.type=='MESH'
verts=[tuple(obj.matrix_world @ v.co) for v in obj.data.vertices]
lower=[(x,y) for x,y,z in verts if abs(z)<1e-5]
def nearest(p, arr): return min(math.hypot(p[0]-q[0],p[1]-q[1]) for q in arr)
errs=[nearest(p,lower) for p in source]
reverse=[nearest(p,source) for p in lower]
bounds=[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)]
with open(blend,'rb') as f: sha=hashlib.sha256(f.read()).hexdigest()
report={'asset_sha256':sha,'gis_feature_id':gj['features'][0]['id'],'gis_props':gj['features'][0]['properties'],'model_shell_name':obj.name,'model_shell_vertex_count':len(verts),'lower_shell_vertex_count':len(lower),'source_vertex_count':len(source),'source_to_shell_max_vertex_error_m':max(errs),'shell_to_source_max_vertex_error_m':max(reverse),'shell_bounds_m':bounds}
out=os.path.join(os.path.dirname(__file__),'footprint_probe.json')
with open(out,'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
