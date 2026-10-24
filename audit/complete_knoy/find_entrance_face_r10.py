import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
o=bpy.data.objects['KNOY_Exterior_Masonry_Walls'];
for p in o.data.polygons:
 c=o.matrix_world@p.center
 if abs(c.y+46.58)<.15 and -1<c.x<2 and 3<c.z<5:
  print('poly',p.index,'center',tuple(round(v,3) for v in c),'normal',tuple(round(v,2) for v in (o.matrix_world.to_3x3()@p.normal)),'mat',o.data.materials[p.material_index].name,'area',round(p.area,3))
