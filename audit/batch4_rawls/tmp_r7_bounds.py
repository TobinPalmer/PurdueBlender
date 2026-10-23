import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
for name in ['RAWL_Masonry_Exterior_Walls','RAWL_Atrium_Structural_Columns']:
 o=bpy.data.objects[name];cs=[o.matrix_world@Vector(v) for v in o.bound_box];print(name, [round(min(v[i] for v in cs),2) for i in range(3)],[round(max(v[i] for v in cs),2) for i in range(3)])
