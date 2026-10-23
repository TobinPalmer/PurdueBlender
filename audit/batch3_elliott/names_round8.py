import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend')
c=bpy.data.collections['Asset_elliott_hall_of_music']
for o in c.objects:
 if any(x in o.name.lower() for x in ('hovde','door','entry','canopy','connector')): print(o.name, o.type)
