import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/purdue_campus_master.blend')
print('N',len(bpy.data.objects))
for o in bpy.data.objects:
 if 'elliott' in o.name.lower() or 'hovde' in o.name.lower(): print(o.name,o.type,tuple(round(x,4) for x in o.location))
