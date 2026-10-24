import bpy
m=bpy.data.materials['KRACH_LEADERSHIP_CENTER | evidence palette textured masonry']
for n in m.node_tree.nodes:
 print(n.name,n.bl_idname)
 for i in n.inputs:
  if hasattr(i,'default_value'):
   try: print(' ',i.name,tuple(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value)
   except: pass
for l in m.node_tree.links: print('LINK',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
