import bpy
from mathutils import Vector
p=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend';bpy.ops.wm.open_mainfile(filepath=p);c=bpy.data.collections['Asset_hovde_hall'];r=bpy.data.objects['HOVD_Root']
print('root',list(r.location),list(r.rotation_euler),list(r.scale))
for o in c.all_objects:
 if o.type=='MESH' and any(k in o.name.lower() for k in ['shell','wall','footprint','wing','core','envelope','building','massing','facade']):
  bb=[r.matrix_world@o.matrix_world@Vector(v) for v in o.bound_box]
  bounds=[[round(min(v[i] for v in bb),2),round(max(v[i] for v in bb),2)] for i in range(3)]
  print(o.name, 'loc',tuple(round(v,2) for v in o.location),'dim',tuple(round(v,2) for v in o.dimensions),'bounds world',bounds)
