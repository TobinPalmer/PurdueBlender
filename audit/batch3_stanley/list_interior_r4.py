import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/stanley_coulter_hall.blend')
for o in bpy.data.collections['SC_Interior_Shell'].objects:
 if not (o.name.startswith('SC_Shell_Floor') or o.name.startswith('SC_GradHub')):
  print(o.name)
