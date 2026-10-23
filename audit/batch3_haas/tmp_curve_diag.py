import bpy
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall']
for o in C.objects:
 if o.type!='CURVE':continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box];mi=[min(q[i] for q in p) for i in range(3)];ma=[max(q[i] for q in p) for i in range(3)]
 if ma[2]>3.5 and mi[2]<6.7: print(o.name,tuple(round(x,2) for x in mi),tuple(round(x,2) for x in ma))
