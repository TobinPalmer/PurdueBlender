import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend');o=bpy.data.objects['RAWL_Masonry_Exterior_Walls']
for pi in [24,25,28,29,32,33]:
 p=o.data.polygons[pi];pts=[o.matrix_world@o.data.vertices[i].co for i in p.vertices];print(pi,[[round(v.x,3),round(v.y,3),round(v.z,3)] for v in pts])
