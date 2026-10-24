import bpy
from mathutils import Vector
from pathlib import Path
p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\morgan_j_burke_boilermaker_aquatic_center.blend')
bpy.ops.wm.open_mainfile(filepath=str(p)); coll=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center']
data=bpy.data.cameras.new('AQUA R4 | north masonry detail camera'); cam=bpy.data.objects.new('AQUA R4 | north masonry detail camera',data); coll.objects.link(cam); cam.location=(15,86,9); cam.rotation_euler=(Vector((5,51.2,6.4))-cam.location).to_track_quat('-Z','Y').to_euler(); data.lens=52
bpy.ops.wm.save_as_mainfile(filepath=str(p));print('Saved R4 masonry detail camera')
