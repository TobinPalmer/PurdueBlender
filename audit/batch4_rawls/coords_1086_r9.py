import bpy
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=str(Path(__file__).with_name('rawls_hall_r9_candidate.blend')))
for n in ['RAWL_2026_1086_Chair','RAWL_2026_1086_Desk','RAWL_2026_Plan1086_00_00','RAWL_2026_Plan1086_04_00']:
 o=bpy.data.objects[n];print(n,'loc',tuple(o.location),'world',tuple(o.matrix_world.translation),'parent',o.parent.name if o.parent else None,'inv',tuple(o.matrix_parent_inverse[i][3] for i in range(3)))
 ps=[o.matrix_world@Vector(c) for c in o.bound_box];print([[min(p[i] for p in ps),max(p[i] for p in ps)] for i in range(3)])
