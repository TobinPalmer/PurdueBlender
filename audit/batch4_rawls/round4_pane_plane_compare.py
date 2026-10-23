import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend');o=bpy.data.objects['RAWL_North_Windows_Glass'];
for p in o.data.polygons:
 c=sum((o.matrix_world@o.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices)
 if c.z<5:
  yout=20.193+(c.x+21.394)*(.597/54.727);print(round(c.x,2),round(c.y,3),round(yout,3),'delta',round(c.y-yout,3))
