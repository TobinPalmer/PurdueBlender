import bpy
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall']
for o in C.objects:
 try:p=[o.matrix_world@Vector(v) for v in o.bound_box];mi=[min(q[i] for q in p) for i in range(3)];ma=[max(q[i] for q in p) for i in range(3)]
 except:continue
 if mi[0]<-26.22 and ma[2]>3 and mi[2]<7: print(o.name,o.type,tuple(round(x,2) for x in mi),tuple(round(x,2) for x in ma))
