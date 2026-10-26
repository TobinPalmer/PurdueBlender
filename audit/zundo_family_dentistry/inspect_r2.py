import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/zundo_family_dentistry_r2.blend')
for n in ['Practice sign panel','Zundo Family Dentistry sign lettering','Street entry glazed door','Projecting entry canopy, inferred','Address lettering 1827']:
 o=bpy.data.objects.get(n)
 print(n, o, 'loc',tuple(o.location),'rot',tuple(o.rotation_euler),'dims',tuple(o.dimensions),'hidden',o.hide_render if o else '-')
 print('matrix', tuple(o.matrix_world.translation) if o else '-')
