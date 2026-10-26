import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\rawls_hall.blend')
for m in bpy.data.materials: print(m.name)
