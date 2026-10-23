import bpy
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall']
for o in C.objects:
 if o.type!='MESH':continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box];mn=[min(q[i] for q in p) for i in range(3)];mx=[max(q[i] for q in p) for i in range(3)]
 if mx[2]>11.5:print(o.name,[[round(v,2) for v in mn],[round(v,2) for v in mx]],[m.name if m else None for m in o.data.materials])
