import bpy
from mathutils import Vector
c=bpy.data.collections['Asset_felix_haas_hall']
for o in c.objects:
 if o.name.startswith('HAAS_Plan_'):
  ps=[o.matrix_world@Vector(v) for v in o.bound_box];mn=[min(p[i] for p in ps) for i in range(3)];mx=[max(p[i] for p in ps) for i in range(3)]
  if any(k in o.name.lower() for k in ['partition','wall','door','stair','desk','label']):print(o.name,[(round(mn[i],2),round(mx[i],2)) for i in range(3)])
