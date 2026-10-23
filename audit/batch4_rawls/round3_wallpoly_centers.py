import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend');o=bpy.data.objects['RAWL_Masonry_Exterior_Walls']
vs=[o.matrix_world@v.co for v in o.data.vertices];print('v bounds',[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)])
for p in o.data.polygons:
 c=sum((o.matrix_world@o.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices)
 print(p.index,tuple(round(v,2) for v in c),round(p.area,1))
