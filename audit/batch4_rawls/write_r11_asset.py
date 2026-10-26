import bpy
src=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batch4_rawls\rawls_hall_r11_candidate.blend'
out=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\rawls_hall.blend'
bpy.ops.wm.open_mainfile(filepath=src)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=out)
print('R11_WRITTEN',bpy.data.filepath)
