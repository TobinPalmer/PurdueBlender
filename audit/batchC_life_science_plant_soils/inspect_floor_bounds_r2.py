import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/life_science_plant_and_soils_laboratory.blend')
for o in bpy.data.objects:
 if 'floor plate' in o.name:
  pts=[o.matrix_world@Vector(v) for v in o.bound_box]
  print(o.name,[(round(min(p[i] for p in pts),2),round(max(p[i] for p in pts),2)) for i in range(3)])
