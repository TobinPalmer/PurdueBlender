import bpy
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall']
for o in C.objects:
 if any(x in o.name for x in ['Beltcourse','Cornice','Water_Table']):
  p=[o.matrix_world@Vector(v) for v in o.bound_box];mi=[min(q[i] for q in p) for i in range(3)];ma=[max(q[i] for q in p) for i in range(3)]
  print(o.name,tuple(round(x,2) for x in mi),tuple(round(x,2) for x in ma))
