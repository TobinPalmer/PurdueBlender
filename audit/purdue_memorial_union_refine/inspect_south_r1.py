import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\purdue_memorial_union.blend')
col=bpy.data.collections['Asset_purdue_memorial_union']
for o in col.all_objects:
 if o.type not in {'MESH','CURVE','FONT'}: continue
 pts=[o.matrix_world @ Vector(c) for c in o.bound_box]
 lo=[min(v[i] for v in pts) for i in range(3)]; hi=[max(v[i] for v in pts) for i in range(3)]
 if lo[1] < -25 and hi[1] < -20 and lo[2] < 18 and hi[2] > 3 and not any(k in o.name for k in ('Base','Wall','Roof','Beltcourse','Ceiling')):
  print(f'{o.name:45} {lo[0]:7.2f}:{hi[0]:7.2f} {lo[1]:7.2f}:{hi[1]:7.2f} {lo[2]:6.2f}:{hi[2]:6.2f}')
