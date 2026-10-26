import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];bpy.ops.wm.open_mainfile(filepath=str(Path(__file__).with_name('rawls_hall_r9_candidate.blend')))
for o in bpy.data.objects:
 if o.type=='MESH' and any(k in o.name for k in ('Plan1054','Plan1062','Plan1008','Atrium','FloorSlab')):
  ps=[o.matrix_world@Vector(c) for c in o.bound_box];print(o.name, [[round(min(p[i] for p in ps),2),round(max(p[i] for p in ps),2)] for i in range(3)])
