import bpy
p=r'modular/buildings/materials_science_and_electrical_engineering_msee.blend';bpy.ops.wm.open_mainfile(filepath=p)
m=bpy.data.materials['materials_science_and_electrical_engineering_msee_facade']
for n in m.node_tree.nodes:
 print(n.name,n.type)
 if n.type in {'TEX_NOISE','BUMP','VALTORGB','TEX_BRICK','TEX_COORD','MAPPING'}:
  print(' ',[(i.name, str(getattr(i,'default_value',None))[:80]) for i in n.inputs])
for o in bpy.data.collections['Asset_materials_science_and_electrical_engineering_msee'].all_objects:
 if o.name.startswith('MSEE_window_') and o.name.endswith('_0'):
  print('window object location/scale/rot',o.location[:],o.scale[:],o.dimensions[:],o.rotation_euler[:])
