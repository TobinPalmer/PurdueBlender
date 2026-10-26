import bpy,os
for p in [r'modular/buildings/bell_tower.blend',r'modular/buildings/felix_haas_hall.blend',r'modular/buildings/psychological_sciences.blend']:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p)); print('\n',os.path.basename(p))
 for m in bpy.data.materials:
  if 'roof' in m.name.lower() and m.node_tree:
   pr=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
   print(m.name, 'base', tuple(round(x,3) for x in pr.inputs['Base Color'].default_value) if pr and not pr.inputs['Base Color'].is_linked else 'linked')
   if pr:
    print(' color link',[(l.from_node.name,l.from_socket.name) for l in m.node_tree.links if l.to_socket==pr.inputs['Base Color']])
    print('nodes',[(n.name,n.type) for n in m.node_tree.nodes])
