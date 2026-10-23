import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend');o=bpy.data.objects['RAWL_Masonry_Exterior_Walls'];print('mods',[(m.name,m.type) for m in o.modifiers]);print('loc',tuple(o.location),'rot',tuple(o.rotation_euler),'scale',tuple(o.scale),'matrix',o.matrix_world)
