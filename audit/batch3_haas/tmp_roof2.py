import bpy
m=bpy.data.materials['HAAS_GooglePhotos_RedClayTiles_estimated']
for n in m.node_tree.nodes:
 if n.type=='TEX_BRICK':
  for k in ['Color1','Color2','Mortar','Scale','Mortar Size']:
   print(k,n.inputs[k].default_value)
for l in m.node_tree.links:print(l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
