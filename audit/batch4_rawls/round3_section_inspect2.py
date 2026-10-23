import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend');
for nm in ['RAWL_Masonry_Exterior_Walls','RAWL_North_Windows_Glass','RAWL_North_Windows_LimestoneSills']:
 o=bpy.data.objects[nm];print('\n',nm)
 for p in o.data.polygons:
  vs=[o.matrix_world@o.data.vertices[i].co for i in p.vertices];c=sum((o.matrix_world@o.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices)
  if 23<c.x<27 and -0.2<c.z<4.2:
   print('poly',p.index,'center',[round(c.x,2),round(c.y,3),round(c.z,2)],'area',round(p.area,2),'bbox',[[round(min(v[i] for v in vs),3),round(max(v[i] for v in vs),3)] for i in range(3)])
