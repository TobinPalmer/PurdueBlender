import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend');r=bpy.data.objects['HOVD_Root'];inv=r.matrix_world.inverted()
for o in bpy.data.collections['Asset_hovde_hall'].all_objects:
 if o.name.startswith(('HOVD_Grand_Step','HOVD_Plaza')):
  ps=[inv@o.matrix_world@Vector(v)for v in o.bound_box];print(o.name,[(min(p[i]for p in ps),max(p[i]for p in ps))for i in [0,1]])
