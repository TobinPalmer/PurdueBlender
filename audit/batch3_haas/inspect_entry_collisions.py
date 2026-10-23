import bpy
from mathutils import Vector
c=bpy.data.collections['Asset_felix_haas_hall']
for o in c.objects:
 pts=[o.matrix_world@Vector(v) for v in o.bound_box]
 mn=[min(p[i] for p in pts) for i in range(3)];mx=[max(p[i] for p in pts) for i in range(3)];d=[mx[i]-mn[i] for i in range(3)];ctr=[(mx[i]+mn[i])/2 for i in range(3)]
 if 11<ctr[0]<15 and abs(ctr[1])<10 and ctr[2]<5 and d[1]>1.5 and d[2]>0.5:print(o.name,'center',[round(x,2) for x in ctr],'dims',[round(x,2) for x in d])
