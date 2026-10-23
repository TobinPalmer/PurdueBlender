import bpy
from mathutils import Vector
for o in bpy.data.collections['Asset_felix_haas_hall'].objects:
 if 'HAAS_Photo' not in o.name:continue
 ps=[o.matrix_world@Vector(v) for v in o.bound_box];mn=[min(p[i] for p in ps) for i in range(3)];mx=[max(p[i] for p in ps) for i in range(3)]
 if mn[0]>12.5 and mx[0]<13.5 and mn[2]>4.5:print(o.name,[(round(mn[i],2),round(mx[i],2)) for i in range(3)])
