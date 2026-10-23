import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
for n in ['RAWL_FloorSlab_L1_Ground','RAWL_FloorSlab_L2','RAWL_FloorSlab_L3','RAWL_FloorSlab_L4','RAWL_FloorSlab_L5']:
 o=bpy.data.objects[n]; data=o.data; data.calc_loop_triangles()
 arr=[]
 for p in data.polygons:
  c=o.matrix_world@p.center; no=o.matrix_world.to_3x3()@p.normal
  if 2<=c.x<=19 and -5<=c.y<=3 and no.z>.9: arr.append([round(c.x,1),round(c.y,1),round(c.z,1),round(p.area,2),p.material_index])
 print(n, len(arr), arr[:20])
