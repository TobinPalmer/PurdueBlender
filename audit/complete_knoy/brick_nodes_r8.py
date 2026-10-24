import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend';bpy.ops.wm.open_mainfile(filepath=p);m=bpy.data.materials['KNOY_Purdue_Red_Brick']
for n in m.node_tree.nodes:
 print(n.name,n.type,'op',getattr(n,'operation',None),'data_type',getattr(n,'data_type',None),'blend',getattr(n,'blend_type',None),'clamp',getattr(n,'clamp_factor',None), 'fac',getattr(n,'factor',None))
 for i in n.inputs:
  if i.is_linked: print('  ',i.name,'link',[(l.from_node.name,l.from_socket.name) for l in m.node_tree.links if l.to_socket==i])
