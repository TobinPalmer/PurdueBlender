import bpy, os
for p in [r'modular/buildings/hovde_hall.blend',r'modular/buildings/hansen_life_sciences.blend',r'modular/buildings/knoy_hall.blend']:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p))
 print('\nFILE',p)
 for m in bpy.data.materials:
  if m.users and m.use_nodes:
   bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
   if bs:
    col=tuple(round(x,2) for x in bs.inputs['Base Color'].default_value[:3]); print(m.name, 'users',m.users,'color',col,'metal',round(bs.inputs['Metallic'].default_value,2),'rough',round(bs.inputs['Roughness'].default_value,2),'nodes',len(m.node_tree.nodes))
