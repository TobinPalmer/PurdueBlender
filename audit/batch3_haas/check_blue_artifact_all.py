import bpy
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall']
for o in C.objects:
 if o.type!='MESH':continue
 mats=[m for m in getattr(o.data,'materials',[]) if m]
 if not any(any(k in m.name.lower() for k in ['glass','window','blue','cyan']) for m in mats):continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box];mn=[min(q[i] for q in p) for i in range(3)];mx=[max(q[i] for q in p) for i in range(3)]
 print(o.name, [[round(v,1) for v in mn],[round(v,1) for v in mx]],[m.name for m in mats])
