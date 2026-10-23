import bpy,json
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall'];rows=[]
for o in C.objects:
 if o.type!='MESH' or not o.data.materials:continue
 if not any(m and ('BlueGlass' in m.name or 'Glass' in m.name) for m in o.data.materials):continue
 ps=[o.matrix_world@Vector(v) for v in o.bound_box];mi=[min(q[i] for q in ps) for i in range(3)];ma=[max(q[i] for q in ps) for i in range(3)]
 if mi[0]>-1 and ma[0]<13.5:
  rows.append((o.name,[[round(x,2) for x in mi],[round(x,2) for x in ma]],[m.name for m in o.data.materials]))
print(json.dumps(rows,indent=2))
