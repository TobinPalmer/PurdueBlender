import bpy
from mathutils import Vector
c=bpy.data.collections['Asset_felix_haas_hall']
for o in c.objects:
 ps=[o.matrix_world@Vector(v) for v in o.bound_box]; mn=[min(p[i] for p in ps) for i in range(3)]; mx=[max(p[i] for p in ps) for i in range(3)]
 if mn[0]>12.5 and mx[0]<13.5 and mx[2]>1 and mn[2]<10.5:
  print(o.name,[(round(mn[i],2),round(mx[i],2)) for i in range(3)], [m.name if m else '' for m in getattr(o.data,'materials',[])])
