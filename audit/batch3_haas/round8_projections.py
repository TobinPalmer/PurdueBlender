import bpy,json
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall'];r=[]
for o in C.objects:
 if o.type!='MESH' or o.name.startswith('HAAS_Plan_'):continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box];mi=[min(q[i] for q in p) for i in range(3)];ma=[max(q[i] for q in p) for i in range(3)]
 if mi[1]<-26.05 or ma[1]>26.80 or mi[0]<-26.25 or ma[0]>13.35:
  if ('Stair_Tread' in o.name or 'Roof' in o.name or 'West' in o.name or 'Pier' in o.name or 'Lintel' in o.name or 'Sill' in o.name or 'Pavilion' in o.name or 'Entry' in o.name):continue
  r.append((o.name,[[round(x,2) for x in mi],[round(x,2) for x in ma]]))
print(json.dumps(r,indent=2))
