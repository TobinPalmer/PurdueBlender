import bpy
from mathutils import Vector
c=bpy.data.collections['Asset_felix_haas_hall']
for o in c.objects:
 if any(k in o.name.lower() for k in ['facade','brick','pier','band','entry','main_door','window']):
  ps=[o.matrix_world@Vector(v) for v in o.bound_box]; mn=[min(p[i] for p in ps) for i in range(3)]; mx=[max(p[i] for p in ps) for i in range(3)]
  print(o.name, tuple(round(v,2) for v in mn),tuple(round(v,2) for v in mx), [m.name if m else '' for m in getattr(o.data,'materials',[])])
