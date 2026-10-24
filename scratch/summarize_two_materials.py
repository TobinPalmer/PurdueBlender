import bpy, os
for fn in ['mccutcheon_hall.blend','niswonger_aviation_tech.blend']:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(os.path.join('modular','buildings',fn)))
 print('\nFILE',fn)
 for m in bpy.data.materials:
  if not m.node_tree: continue
  p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if p:
   print(m.name,'base_link',p.inputs['Base Color'].is_linked,'rough',round(p.inputs['Roughness'].default_value,2),'nodes',len(m.node_tree.nodes))
