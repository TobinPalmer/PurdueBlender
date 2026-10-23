import bpy,json
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall']; rows=[]
for o in C.objects:
 if o.type!='MESH':continue
 ps=[o.matrix_world@Vector(v) for v in o.bound_box];mi=[min(q[i] for q in ps) for i in range(3)];ma=[max(q[i] for q in ps) for i in range(3)]
 if mi[0]>1.5 and ma[0]<3.8 and ma[2]>1.5 and mi[2]<10:
  rows.append({'n':o.name,'b':[[round(x,2) for x in mi],[round(x,2) for x in ma]],'m':[m.name for m in o.data.materials]})
print(json.dumps(rows,indent=2))
