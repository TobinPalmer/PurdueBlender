import bpy
m=bpy.data.materials['RAWL_Purdue_Red_Brick'];nt=m.node_tree
for n in nt.nodes:
 print('\nNODE',n.name,n.type)
 for s in n.inputs:
  if s.is_linked:print(' IN',s.name,'<-',[(l.from_node.name,l.from_socket.name) for l in s.links])
  elif s.name in {'X','Y','Z','Scale','Brick Width','Row Height','Color1','Color2','Mortar Size'}:print(' IN',s.name,s.default_value)
 for s in n.outputs:
  if s.is_linked:print(' OUT',s.name,'->',[(l.to_node.name,l.to_socket.name) for l in s.links])
