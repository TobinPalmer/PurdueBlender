import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend')
print([m.name for m in bpy.data.materials if 'carpet' in m.name.lower()])
print([(o.name,len(o.data.vertices)) for o in bpy.data.collections['Asset_elliott_hall_of_music'].objects if o.name.startswith('ELLT_EXT_Sculpture_') and o.name.endswith('_Heroic_Figure')])
