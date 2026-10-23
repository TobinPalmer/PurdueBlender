import bpy,json
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall'];r=[]
for o in C.objects:
 if o.type!='MESH' or o.name.startswith('HAAS_Plan_'):continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box];mi=[min(q[i] for q in p) for i in range(3)];ma=[max(q[i] for q in p) for i in range(3)]
 if ma[0]>12.98 and ma[2]>4.5 and mi[2]<6.5:
  r.append((o.name,round(mi[0],2),round(ma[0],2),round(mi[1],2),round(ma[1],2),round(mi[2],2),round(ma[2],2)))
print(json.dumps(r,indent=2))
