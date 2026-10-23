import bpy
m=bpy.data.materials['Purdue_Red_Brick.001']
for n in m.node_tree.nodes:print(n.name,n.type,[(i.name,tuple(i.default_value) if hasattr(i,'default_value') and hasattr(i.default_value,'__len__') else getattr(i,'default_value',None)) for i in n.inputs if i.name in ['Base Color','Scale','Color1','Color2','Mortar','Vector']])
for l in m.node_tree.links: print(l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
