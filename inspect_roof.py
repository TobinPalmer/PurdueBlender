import bpy,os
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(r'modular/buildings/felix_haas_hall.blend'))
m=bpy.data.materials['HAAS_Slate_Roof']
for n in m.node_tree.nodes:
 print(n.name,n.type)
 for i in n.inputs:
  if i.is_linked: print(' ',i.name,'<-',[(l.from_node.name,l.from_socket.name) for l in m.node_tree.links if l.to_socket==i])
