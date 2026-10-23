import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
for name in ['Bedford_Indiana_Limestone','Historic_Slate_Roof_Procedural','Architectural_Glazing']:
 m=bpy.data.materials[name];print('\n',name)
 for l in m.node_tree.links:
  print(l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
 for n in m.node_tree.nodes:
  if n.type in {'MIX','TEX_NOISE','TEX_WAVE','BUMP','BSDF_PRINCIPLED'}:
   print('node',n.name,n.type)
   for i in n.inputs:
    if not i.is_linked and hasattr(i,'default_value'):
     print(' ',i.name,i.default_value)
