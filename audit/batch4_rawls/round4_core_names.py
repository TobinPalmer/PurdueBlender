import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
for o in bpy.data.objects:
 if '1008' in o.name or 'NorthStair' in o.name:print(o.name)
