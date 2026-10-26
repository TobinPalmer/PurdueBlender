import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/stanley_coulter_hall.blend')
for row in ['Level0_Basement','Level1_FirstFloor','Level2_SecondFloor','Level3_ThirdFloor']:
 print('\n',row)
 for o in bpy.data.objects:
  if o.type=='MESH' and o.name.startswith('SC_Win_East_') and row in o.name and o.name.endswith('_GlassPane'):
   pts=[o.matrix_world@v.co for v in o.data.vertices];ys=[p.y for p in pts];zs=[p.z for p in pts];print(o.name,round((min(ys)+max(ys))/2,2),round(max(ys)-min(ys),2),round((min(zs)+max(zs))/2,2),round(max(zs)-min(zs),2))
