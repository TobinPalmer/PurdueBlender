import bpy
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall']
for o in C.objects:
 pts=[o.matrix_world@Vector(v) for v in o.bound_box] if o.type=='MESH' else []
 if not pts:continue
 mn=[min(p[i] for p in pts) for i in range(3)];mx=[max(p[i] for p in pts) for i in range(3)]
 if mn[0]>1 and mn[1]>24 and 4<mx[2]<10:
  mats=[m.name for m in getattr(o.data,'materials',[]) if m]
  if any('glass' in m.lower() or 'blue' in m.lower() or 'window' in o.name.lower() for m in mats+ [o.name]): print(o.name,[[round(v,2) for v in mn],[round(v,2) for v in mx]],mats)
