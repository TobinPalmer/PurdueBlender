import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
for nm in ['RAWL_Masonry_Exterior_Walls','RAWL_North_Windows_Glass','RAWL_North_Windows_BronzeMullions']:
 o=bpy.data.objects[nm]; vs=[o.matrix_world@v.co for v in o.data.vertices]
 print('\n',nm,'poly',len(o.data.polygons))
 for z in [1,4,7,10,13,16,19]:
  pts=[v for v in vs if abs(v.z-z)<.3 and v.x>20 and v.x<35]
  if pts:print(z, 'x',[round(min(v.x for v in pts),2),round(max(v.x for v in pts))], 'y',[round(min(v.y for v in pts),3),round(max(v.y for v in pts))])
 print('materials',[(m.name,m.diffuse_color[:]) for m in o.data.materials])
