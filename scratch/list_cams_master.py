import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend')
for o in bpy.data.objects:
 if o.type=='CAMERA': print(o.name,tuple(round(v,2) for v in o.location),tuple(round(v,2) for v in o.rotation_euler),o.data.lens)
