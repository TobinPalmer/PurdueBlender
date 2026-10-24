import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
for mn in ['KNOY_Precast_Concrete','KNOY_Plaza_Concrete']:
 m=bpy.data.materials[mn];print(mn)
 for n in m.node_tree.nodes:
  if n.type=='MIX':
   print('mix',n.data_type)
   for i,s in enumerate(n.inputs):
    if hasattr(s,'default_value'):
     try: v=tuple(s.default_value)
     except: v=s.default_value
     print(i,s.name,v)
 print('links',[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links])
