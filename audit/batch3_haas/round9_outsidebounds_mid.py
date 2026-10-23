import bpy
from mathutils import Vector
for o in bpy.data.objects:
 if o.name.startswith('HAAS_Plan_') or o.type in {'LIGHT','CAMERA'}:continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 if not p:continue
 mi=[min(q[i] for q in p) for i in range(3)];ma=[max(q[i] for q in p) for i in range(3)]
 if (mi[0]<-26.22 or ma[0]>12.981 or mi[1]<-25.98 or ma[1]>26.76) and ma[2]>4.5 and mi[2]<6.5:
  print(o.type,o.name,tuple(round(x,2) for x in mi),tuple(round(x,2) for x in ma),'cols',[c.name for c in o.users_collection])
