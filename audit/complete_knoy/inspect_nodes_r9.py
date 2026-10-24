import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
for name in ['KNOY_Purdue_Red_Brick','KNOY_Precast_Concrete','KNOY_Dark_Tinted_Glass']:
 m=bpy.data.materials.get(name); print('MATERIAL',name)
 for n in m.node_tree.nodes:
  print(n.name,n.type, 'in',[(s.name, s.is_linked, (tuple(s.default_value) if hasattr(s.default_value,'__len__') else s.default_value) if hasattr(s,'default_value') else None) for s in n.inputs if s.is_linked or s.name in ['Scale','Detail','Color1','Color2','Mortar','Brick Width','Row Height','Mortar Size','Roughness','Base Color','Distance','Strength']])
 for l in m.node_tree.links: print(' LINK',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
