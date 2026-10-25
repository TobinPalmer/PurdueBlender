import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\purdue_memorial_union.blend')
for o in bpy.data.collections['Asset_purdue_memorial_union'].all_objects:
 if 'Roof' in o.name:
  pts=[o.matrix_world@Vector(c) for c in o.bound_box]
  b=[[round(min(v[i] for v in pts),2),round(max(v[i] for v in pts),2)] for i in range(3)]
  print(o.name,b,[(m.name if m else None,tuple(round(x,2) for x in m.diffuse_color) if m else None) for m in o.data.materials])
