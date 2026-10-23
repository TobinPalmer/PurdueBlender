import bpy
for o in bpy.data.objects:
 if 'Roof' in o.name or 'roof' in o.name or 'Cupola' in o.name:
  print('\n',o.name,[m.name if m else None for m in getattr(o.data,'materials',[])])
  for m in getattr(o.data,'materials',[]):
   if m and m.use_nodes:
    p=m.node_tree.nodes.get('Principled BSDF')
    if p:print('  base',tuple(p.inputs['Base Color'].default_value),'links',[(l.from_node.name,l.from_socket.name) for l in p.inputs['Base Color'].links])
