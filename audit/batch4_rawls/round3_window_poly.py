import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
for n in ['RAWL_North_Windows_Glass','RAWL_North_Windows_BronzeMullions']:
 o=bpy.data.objects[n];print(n,'loc',list(o.location),'polygons',len(o.data.polygons),'mat',[(m.name,m.blend_method if hasattr(m,'blend_method') else '') for m in o.data.materials]);
 for p in list(o.data.polygons)[:3]:
  print('poly area',p.area,'normal',list(p.normal),'verts',[list(o.matrix_world@o.data.vertices[i].co) for i in p.vertices])
