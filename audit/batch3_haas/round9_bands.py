import bpy
from mathutils import Vector
for o in bpy.data.objects:
 if 'Band' not in o.name:continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 if not p:continue
 mi=[min(q[i] for q in p) for i in range(3)];ma=[max(q[i] for q in p) for i in range(3)]
 if ma[2]>4.5 and mi[2]<6.0:print(o.name,tuple(round(x,2) for x in mi),tuple(round(x,2) for x in ma),o.hide_render)
