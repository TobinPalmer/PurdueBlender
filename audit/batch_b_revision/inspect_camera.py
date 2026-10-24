import bpy
from pathlib import Path
for k,f in [('brees','brees_student_athletic_academic_center.blend'),('ford','ford_dining_court.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings')/f)); c=bpy.context.scene.camera; print(k,c.name,tuple(c.location),tuple(c.rotation_euler),c.data.lens)
