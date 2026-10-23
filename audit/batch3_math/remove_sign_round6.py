import bpy
from pathlib import Path
p=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/math_sciences.blend')
bpy.ops.wm.open_mainfile(filepath=str(p))
obj=bpy.data.objects.get('MATH_Signage_East')
print('before', bool(obj), (obj.location[:], obj.dimensions[:]) if obj else None)
if obj:
    bpy.data.objects.remove(obj, do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(p))
