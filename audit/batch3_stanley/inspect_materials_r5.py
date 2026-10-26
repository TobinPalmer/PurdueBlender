import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/stanley_coulter_hall.blend')
for n in ['Lantern_Warm_Glow','Bedford_Indiana_Limestone','Purdue_Red_Brick_Procedural']:
 m=bpy.data.materials.get(n);print('\nMATERIAL',n,'diff',list(m.diffuse_color) if m else None)
 if m and m.use_nodes:
  for node in m.node_tree.nodes:
   if node.type=='BSDF_PRINCIPLED':
    for key in ['Base Color','Roughness','Metallic','Emission Color','Emission Strength']:
     if key in node.inputs: print(key,node.inputs[key].default_value)
