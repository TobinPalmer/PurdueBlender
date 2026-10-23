import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
for o in bpy.data.objects:
 if o.name.startswith('RAWL_2026_Plan') or 'FloorSlab' in o.name:
  bb=[o.matrix_world@Vector(v) for v in o.bound_box]; print(o.name, [round(min(v[i] for v in bb),1) for i in range(3)],[round(max(v[i] for v in bb),1) for i in range(3)])
