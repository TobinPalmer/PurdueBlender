import bpy, json
p=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend'
bpy.ops.wm.open_mainfile(filepath=p)
c=bpy.data.collections['Asset_elliott_hall_of_music']
for o in c.objects:
 print(o.name,o.type,tuple(round(v,2) for v in o.location), tuple(round(v,2) for v in o.dimensions))
