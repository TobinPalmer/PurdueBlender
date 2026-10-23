import bpy
m=bpy.data.materials['HAAS_GooglePhotos_RedClayTiles_estimated']
for n in m.node_tree.nodes:
 if n.type=='BSDF_PRINCIPLED':
  print('BASE',list(n.inputs['Base Color'].default_value),'EM',list(n.inputs['Emission Color'].default_value),n.inputs['Emission Strength'].default_value)
for l in m.node_tree.links:print(l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
