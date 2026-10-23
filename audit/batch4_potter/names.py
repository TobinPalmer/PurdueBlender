import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend')
c=bpy.data.collections['Asset_potter_engineering']
for o in c.objects:
 if o.type=='MESH':
  print(o.name)
