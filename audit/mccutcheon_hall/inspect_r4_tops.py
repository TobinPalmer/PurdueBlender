import bpy
from mathutils import Vector
asset=bpy.data.collections['Asset_mccutcheon_hall']
for obj in asset.all_objects:
    if obj.type == 'MESH':
        top=max((obj.matrix_world @ Vector(c)).z for c in obj.bound_box)
        if top > 27.4:
            print(f'{top:.3f}\t{obj.name}')
