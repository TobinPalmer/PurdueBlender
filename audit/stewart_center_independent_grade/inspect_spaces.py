import bpy
from mathutils import Vector
c=bpy.data.collections['Asset_stewart_center']
for prefix in ('HSSE_Main','HSSE_Wall','HSSE_Interior','Ringel_Wall','Loeb_Interior'):
 for o in sorted([o for o in c.all_objects if o.name.startswith(prefix)],key=lambda o:o.name):
  b=[o.matrix_world@Vector(v) for v in o.bound_box]
  print(o.name,[round(min(p[i] for p in b),2) for i in range(3)],[round(max(p[i] for p in b),2) for i in range(3)])
