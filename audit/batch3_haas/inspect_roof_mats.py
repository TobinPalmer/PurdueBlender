import bpy
for n in ['HAAS_Photo_Main_Hipped_Roof','HAAS_Photo_Entrance_Hipped_Roof']:
 o=bpy.data.objects.get(n);print('OBJECT',n,'exists',bool(o))
 if o:print('mat',[(m.name if m else None,tuple(m.diffuse_color) if m else None) for m in o.data.materials], 'parent',o.parent.name if o.parent else None,'loc',tuple(o.location))
for m in bpy.data.materials:
 if 'RedClay' in m.name:
  print('MAT',m.name,'nodes',[(n.name,n.type) for n in m.node_tree.nodes])
  for l in m.node_tree.links:print('link',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
