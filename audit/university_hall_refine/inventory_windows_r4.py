import bpy
from mathutils import Vector
for o in sorted(bpy.data.collections['Asset_university_hall'].all_objects,key=lambda o:o.name):
 if o.type=='MESH' and ('Win' in o.name or 'Window' in o.name) and not o.name.startswith(('UNIV_R4_','UNIV_R5_')):
  b=[o.matrix_world@Vector(c) for c in o.bound_box]
  lo=[min(p[i] for p in b) for i in range(3)];hi=[max(p[i] for p in b) for i in range(3)]
  if lo[2]<13.2: print(o.name, [round(v,2) for v in lo], [round(v,2) for v in hi])
