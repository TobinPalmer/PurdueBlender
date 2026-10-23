import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend')
for o in bpy.data.collections['Asset_elliott_hall_of_music'].objects:
 if o.name.startswith('ELLT_B3_'): print(o.name, o.type, len(o.data.vertices) if o.type=='MESH' else '', [m.name for m in getattr(o.data,'materials',[])])
