import bpy
from mathutils import Vector
for o in bpy.data.objects:
 if 'Step_' in o.name and o.name.startswith('HAAS_'):
  pts=[o.matrix_world@Vector(v) for v in o.bound_box];print(o.name,[[round(min(p[i] for p in pts),2) for i in range(3)],[round(max(p[i] for p in pts),2) for i in range(3)]])
