import bpy
from mathutils import Vector
for o in sorted(bpy.data.objects,key=lambda o:o.name):
 if 'EaveConsole' in o.name or 'ArchedWindow' in o.name or o.name.startswith('UNIV_R4_Mansard_'):
  pts=[o.matrix_world@Vector(c) for c in o.bound_box] if o.type=='MESH' else [o.matrix_world@p.co.xyz for s in o.data.splines for p in s.points]
  if pts: print(o.name,o.type,'dims',tuple(round(v,2) for v in o.dimensions),'bounds',[[round(min(p[i] for p in pts),2),round(max(p[i] for p in pts),2)] for i in range(3)])
