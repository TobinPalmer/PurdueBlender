import bpy,json
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall'];r=[]
for o in C.objects:
 if o.type!='MESH' or 'Pavilion_' not in o.name:continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box];mi=[min(q[i] for q in p) for i in range(3)];ma=[max(q[i] for q in p) for i in range(3)]
 r.append({'n':o.name,'b':[[round(x,2) for x in mi],[round(x,2) for x in ma]],'m':[m.name for m in o.data.materials]})
print(json.dumps(r,indent=2))
