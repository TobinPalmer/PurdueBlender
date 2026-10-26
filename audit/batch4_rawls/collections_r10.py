import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\rawls_hall.blend')
for c in bpy.data.collections:
 print(c.name, len(c.objects), c.children[:])
