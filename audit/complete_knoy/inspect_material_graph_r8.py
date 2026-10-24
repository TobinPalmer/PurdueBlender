import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
for name in ['KNOY_Purdue_Red_Brick','KNOY_Precast_Concrete','KNOY_Dark_Tinted_Glass']:
 m=bpy.data.materials[name];print('\n',name)
 for n in m.node_tree.nodes:
  print(n.name,n.type,[(i.name,tuple(i.default_value) if hasattr(i,'default_value') and hasattr(i.default_value,'__len__') else getattr(i,'default_value',None)) for i in n.inputs if hasattr(i,'default_value')])
 print('LINKS')
 for l in m.node_tree.links:print(l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
