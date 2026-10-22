import bpy,json,os
from mathutils import Vector
c=bpy.data.collections['Asset_beering_hall']
d={}
for o in c.all_objects:
 if o.type=='MESH' and ('Masonry' in o.name or 'Dome' in o.name):
  p=[o.matrix_world@Vector(v) for v in o.bound_box];d[o.name]={'world_center':list(o.matrix_world.translation),'bounds':[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)],'polygons':len(o.data.polygons)}
print(json.dumps(d,indent=2))
