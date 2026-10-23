import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend');c=bpy.data.collections['Asset_elliott_hall_of_music']
for o in c.objects:
 if o.name.startswith('ELLT_B3_'): print(o.name,len(o.data.vertices) if o.type=='MESH' else 0,[m.name for m in getattr(o.data,'materials',[])])
