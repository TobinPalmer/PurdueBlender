import bpy
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=str(Path(__file__).with_name('rawls_hall_r9_candidate.blend')))
for o in bpy.data.objects:
 if o.name.startswith('RAWL_2026_Plan1086_'):
  ps=[o.matrix_world@Vector(c) for c in o.bound_box];print(o.name,[[round(min(p[i] for p in ps),2),round(max(p[i] for p in ps),2)] for i in range(3)])
