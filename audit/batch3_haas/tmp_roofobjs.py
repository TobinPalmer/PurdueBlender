import bpy
from mathutils import Vector
for o in bpy.data.objects:
 if 'roof' in o.name.lower() or 'tile' in o.name.lower():
  try:p=[o.matrix_world@Vector(v) for v in o.bound_box];mi=[min(q[i] for q in p) for i in range(3)];ma=[max(q[i] for q in p) for i in range(3)];bb=tuple(round(x,2) for x in mi+ma)
  except:bb=''
  print(o.name,o.type,[c.name for c in o.users_collection],bb,[m.name if m else None for m in getattr(o.data,'materials',[])])
