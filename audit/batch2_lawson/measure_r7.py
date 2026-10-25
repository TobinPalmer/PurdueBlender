import bpy,json
from mathutils import Vector
coll=bpy.data.collections['Asset_lawson_hall']; names=['LWSN_Foundation_Base','LWSN_Exterior_Brick','LWSN_Limestone_Bands','LWSN_Rotunda_Curtain_Glass','LWSN_Rotunda_Spandrel_Panels','LWSN_Entrance_Canopies','LWSN_Entrance_Plazas']
out={}
for name in names:
 o=bpy.data.objects.get(name)
 if not o: continue
 pts=[o.matrix_world@Vector(c) for c in o.bound_box]
 out[name]={'type':o.type,'bounds':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]], 'dimensions':list(o.dimensions),'location':list(o.location),'rotation':list(o.rotation_euler)}
 if o.type=='MESH':out[name]['vertex_bounds']=[[min(v.co[i] for v in o.data.vertices) for i in range(3)],[max(v.co[i] for v in o.data.vertices) for i in range(3)]]
print(json.dumps(out,indent=2))
