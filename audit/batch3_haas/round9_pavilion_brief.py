import bpy
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall']
for o in C.objects:
 if o.type!='MESH' or not o.name.startswith('HAAS_R5_Pavilion_'):continue
 if 'Band' not in o.name and '_A_' not in o.name and '_B_' not in o.name:continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box];mi=[min(q[i] for q in p) for i in range(3)];ma=[max(q[i] for q in p) for i in range(3)]
 print(o.name,tuple(round(x,2) for x in mi),tuple(round(x,2) for x in ma),[m.name for m in o.data.materials])
