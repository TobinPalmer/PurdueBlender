import bpy
for m in bpy.data.materials:
 if any(k in m.name.lower() for k in ('roof','gravel','ballast','membrane')):
  print('\n',m.name)
  for n in m.node_tree.nodes:
   if n.type=='VALTORGB': print('RAMP',[(e.position,tuple(round(c,4) for c in e.color)) for e in n.color_ramp.elements])
   elif n.type=='TEX_NOISE': print('NOISE',n.label,'scale',n.inputs['Scale'].default_value,'detail',n.inputs['Detail'].default_value,'vector',[(l.from_node.name,l.from_socket.name) for l in m.node_tree.links if l.to_node==n and l.to_socket.name=='Vector'])
