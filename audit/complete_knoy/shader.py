import bpy,json
m=bpy.data.materials['KNOY_Purdue_Red_Brick']
print([(n.name,n.type) for n in m.node_tree.nodes]);print([(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links])
