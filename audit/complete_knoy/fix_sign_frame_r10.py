import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/knoy_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections['Asset_knoy_hall']
wall=bpy.data.objects['KNOY_Exterior_Masonry_Walls']
sign=bpy.data.objects['KNOY_Entrance_Sign_Lettering']
# Preserve the raw GIS-coordinate sign transform from the builder and apply the
# same GIS-to-local parent inverse used by the surrounding shell mesh.
sign.matrix_parent_inverse=wall.matrix_parent_inverse.copy()
bpy.context.view_layer.update()
# Save source asset; geometry remains untouched except this new sign placement.
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('Saved corrected sign alignment:', tuple(sign.matrix_world.translation))
