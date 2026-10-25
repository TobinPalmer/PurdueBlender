import bpy
from mathutils import Vector
a=bpy.data.collections['Asset_niswonger_aviation_tech']
for o in sorted(a.all_objects,key=lambda x:x.name):
 if o.type=='MESH' and any(k in o.name.lower() for k in ('roof','hangar','wall','floor','slab','building')):
  p=[o.matrix_world@Vector(c) for c in o.bound_box]
  print(o.name, tuple(round(min(v[i] for v in p),2) for i in range(3)), tuple(round(max(v[i] for v in p),2) for i in range(3)),len(o.data.materials))
