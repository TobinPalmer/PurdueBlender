import bpy
from pathlib import Path
p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\morgan_j_burke_boilermaker_aquatic_center.blend');bpy.ops.wm.open_mainfile(filepath=str(p))
o=bpy.data.objects['AQUA R2 | 300 individual schematic spectator seats']; mod=o.modifiers.new('AQUA R4 | softened seat pan and back edges','BEVEL'); mod.width=.045; mod.segments=3; mod.limit_method='ANGLE'; mod.angle_limit=.55; mod.harden_normals=True
bpy.ops.wm.save_as_mainfile(filepath=str(p));print('Added small 3-segment seat-edge bevel for a more finished chair silhouette')
