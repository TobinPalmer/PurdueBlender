import bpy,sys,os
for p in sys.argv[sys.argv.index('--')+1:]:
 bpy.ops.wm.open_mainfile(filepath=p); print('\nFILE',os.path.basename(p))
 for m in bpy.data.materials:
  if not m.use_nodes:continue
  ns=m.node_tree.nodes; links=m.node_tree.links
  noises=[n for n in ns if n.type=='TEX_NOISE']
  if not noises:continue
  print('MAT',m.name)
  for n in noises:
   v=n.inputs['Vector']; src=next((l for l in links if l.to_socket==v),None)
   vecsrc=(src.from_node.type,src.from_node.name,src.from_socket.name) if src else ('DEFAULT',tuple(v.default_value))
   outs=[]
   for l in links:
    if l.from_node==n:outs.append((l.to_node.type,l.to_node.name,l.to_socket.name))
   print(' ',n.name,'scale',n.inputs['Scale'].default_value,'detail',n.inputs['Detail'].default_value,'rough',n.inputs['Roughness'].default_value,'vector',vecsrc,'outputs',outs)
