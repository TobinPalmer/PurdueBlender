import bpy
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=str(Path(__file__).with_name('rawls_hall_r9_candidate.blend')))
for n in ['RAWL_2026_Plan1086_02_00','RAWL_2026_Plan1062_Curve_33_00']:
 o=bpy.data.objects[n];print('\n',n)
 for v in o.data.vertices:print([round(x,4) for x in o.matrix_world@v.co])
