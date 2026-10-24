import bpy,os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\rawls_hall.blend')
for c in bpy.data.collections:
 objs=[o for o in c.objects if o.type=='MESH']
 if len(objs)>5:
  pts=[o.matrix_world@Vector(v) for o in objs for v in o.bound_box]
  mn=[min(p[i] for p in pts) for i in range(3)]; mx=[max(p[i] for p in pts) for i in range(3)]
  print(c.name,len(objs),tuple(round(x,1) for x in mn),tuple(round(x,1) for x in mx))
