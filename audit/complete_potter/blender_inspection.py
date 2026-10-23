import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend')
for o in list(bpy.data.collections['Asset_potter_engineering'].objects)[:5]:print(o.name,tuple(o.location),tuple(o.dimensions))
