import bpy,os
for f in ['hovde_hall','hansen_life_sciences','knoy_hall']:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(f'modular/buildings/{f}.blend'))
 print('\n',f)
 for m in bpy.data.materials:
  tagged=[n for n in m.node_tree.nodes if n.get('surface_detail_pass')=='campus_2026_10'] if m.use_nodes else []
  if tagged:
   for n in tagged:
    if n.type=='TEX_NOISE': print(m.name,[(l.to_node.name,l.to_socket.name) for o in n.outputs for l in o.links])
   for n in m.node_tree.nodes:
    if n.label=='Preserve existing relief': print('preserve',m.name,n.inputs['Strength'].default_value,n.inputs['Distance'].default_value, 'connected', n.outputs[0].is_linked)
