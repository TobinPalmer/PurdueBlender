import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend')
for o in bpy.data.collections['Asset_elliott_hall_of_music'].objects:
 if any(k in o.name.lower() for k in ('dock','service','stage','pit','lift','door','aisle','stair')): print(o.name,o.type)
