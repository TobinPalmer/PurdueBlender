import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
for c in bpy.data.objects:
 if c.type=='CAMERA': print(c.name,tuple(round(x,2) for x in c.location),tuple(round(x,3) for x in c.rotation_euler), c.data.type,c.data.lens,c.data.ortho_scale if c.data.type=='ORTHO' else None)
