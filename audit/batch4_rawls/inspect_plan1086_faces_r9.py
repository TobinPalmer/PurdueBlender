import bpy
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=str(Path(__file__).with_name('rawls_hall_r9_candidate.blend')));o=bpy.data.objects['RAWL_2026_Plan1086_02_00'];
for p in o.data.polygons:
 pts=[o.matrix_world@o.data.vertices[i].co for i in p.vertices];print('face',p.index,'normal',tuple(round(v,3) for v in (o.matrix_world.to_3x3()@p.normal).normalized()),'verts',[[round(v,3) for v in q] for q in pts])
