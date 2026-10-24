import bpy
from mathutils import Vector
for o in bpy.data.objects:
 if o.type!='MESH': continue
 if any(k in o.name.lower() for k in ['fountain','plaza','promenade','apron','loeb','founders']):
  bb=[o.matrix_world@Vector(c) for c in o.bound_box]; lo=[min(v[i] for v in bb) for i in range(3)]; hi=[max(v[i] for v in bb) for i in range(3)]; c=[round((lo[i]+hi[i])/2,1) for i in range(3)]
  print(o.name, c, [m.name for m in o.data.materials if m])
