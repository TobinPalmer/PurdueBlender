import bpy,json
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall'];r=[]
for o in C.objects:
 if o.type!='MESH' or o.name.startswith('HAAS_Plan_'):continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box];mi=[min(q[i] for q in p) for i in range(3)];ma=[max(q[i] for q in p) for i in range(3)]
 if ma[0]>13.25 and ma[2]>4.0 and mi[2]<7.0:
  r.append({'n':o.name,'b':[[round(x,2) for x in mi],[round(x,2) for x in ma]],'m':[m.name for m in o.data.materials]})
print(json.dumps(r,indent=2))
