import bpy
from mathutils import Vector
for n in ['HAAS_East_Portal_Stone_Pavilion','HAAS_East_Portal_Pediment','HAAS_East_Portal_Arch_Moulding','HAAS_Memorial_Landing','HAAS_East_Memorial_Plaza']:
 o=bpy.data.objects.get(n)
 if o:
  pts=[o.matrix_world@Vector(v) for v in o.bound_box]
  print(n,'loc',tuple(round(v,2) for v in o.location),'bbox',[[round(min(p[i] for p in pts),2) for i in range(3)],[round(max(p[i] for p in pts),2) for i in range(3)]],'col',[x.name for x in o.users_collection])
