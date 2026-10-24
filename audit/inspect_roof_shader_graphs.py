import bpy
for m in bpy.data.materials:
 if any(k in m.name.lower() for k in ('roof','gravel','ballast','membrane')):
  print('\nMAT',m.name)
  nt=m.node_tree
  for n in nt.nodes:
   if n.type in {'BSDF_PRINCIPLED','TEX_NOISE','BUMP','VALTORGB','TEX_COORD','MAPPING','MATH','MIX_RGB','MAP_RANGE'}:
    print('NODE',n.type,n.name,n.label, {i.name:(tuple(round(x,4) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,4)) for i in n.inputs if not i.is_linked})
  for l in nt.links:
   print('LINK',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
