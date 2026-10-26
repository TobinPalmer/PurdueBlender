import bpy
from mathutils import Vector
for o in sorted(bpy.data.collections['Asset_university_hall'].all_objects,key=lambda o:o.name):
 n=o.name.lower()
 if any(s in n for s in ('column','pillar','support','post')) and o.type=='MESH' and not o.name.startswith(('UNIV_R4_','UNIV_R5_')):
  pts=[o.matrix_world@Vector(c) for c in o.bound_box];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
  print(o.name, [round(v,1) for v in lo],[round(v,1) for v in hi])
