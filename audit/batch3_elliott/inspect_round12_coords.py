import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend')
for n in ['ELLT_B3_seat','ELLT_B3_stair','ELLT_B3_carpet','ELLT_B3_stage']:
 o=bpy.data.objects[n];print(n,'loc',tuple(round(x,2) for x in o.location),'rot',tuple(round(x,2) for x in o.rotation_euler),'scale',tuple(round(x,3) for x in o.scale),'v',len(o.data.vertices))
 print('vtx', [tuple(round(x,2) for x in v.co) for v in o.data.vertices[:4]])
