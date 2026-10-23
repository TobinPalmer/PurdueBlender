import bpy
from mathutils import Vector
for o in bpy.data.objects:
 if o.name.startswith('HAAS_Plan_') or o.type=='LIGHT' or o.type=='CAMERA':continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 if not p:continue
 mi=[min(q[i] for q in p) for i in range(3)];ma=[max(q[i] for q in p) for i in range(3)]
 if ma[0]-mi[0]>3 and ma[2]>4.5 and mi[2]<6.5:
  print(o.type,o.name,tuple(round(x,2) for x in mi),tuple(round(x,2) for x in ma))
