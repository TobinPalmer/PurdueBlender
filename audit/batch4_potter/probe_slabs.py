import bpy
P=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend';bpy.ops.wm.open_mainfile(filepath=P);c=bpy.data.collections['Asset_potter_engineering']
for o in c.objects:
 if 'Interior_Slab' in o.name or 'Official_864_Roof' in o.name:
  zs=[v.co.z for v in o.data.vertices]; print(o.name, min(zs),max(zs),o.data.materials[:])
