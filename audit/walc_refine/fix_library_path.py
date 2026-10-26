import bpy
lib=next(x for x in bpy.data.libraries if 'engineering_foliage_library.blend' in x.filepath)
lib.filepath='//../site/foliage_library/engineering_foliage_library.blend'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath, compress=True)
print('PATH',lib.filepath)
