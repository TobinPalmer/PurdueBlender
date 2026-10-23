import bpy
from mathutils import Vector
for name in ['HAAS_Brick_Wall_East','HAAS_Photo_Entrance_Limestone_Facade']:
 o=bpy.data.objects[name];print('\nOBJ',name,'verts',len(o.data.vertices),'faces',len(o.data.polygons),'bounds',tuple(round(v,3) for v in o.bound_box[0]))
 for p in o.data.polygons:
  cen=o.matrix_world@p.center; normal=o.matrix_world.to_3x3()@p.normal
  if name.endswith('_East') and normal.x>.5 or name.endswith('_Facade') and p.index<8:
   print(p.index,'center',tuple(round(c,2) for c in cen),'normal',tuple(round(c,2) for c in normal),'mat',p.material_index,'area',round(p.area,2))
