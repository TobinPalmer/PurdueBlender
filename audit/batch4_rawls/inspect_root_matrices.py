import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
for n in ['AssetRoot_rawls_hall','RAWL_Atrium_Mezzanine_Balustrades','RAWL_FloorSlab_L1_Ground','RAWL_Masonry_Exterior_Walls']:
 o=bpy.data.objects[n];print(n,'loc',tuple(o.location),'world',tuple(o.matrix_world.translation),'parent',o.parent.name if o.parent else None,'parentinv',tuple(o.matrix_parent_inverse.translation))
