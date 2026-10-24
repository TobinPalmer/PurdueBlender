import bpy,os
for p in [r'modular/buildings/bell_tower.blend',r'modular/buildings/felix_haas_hall.blend',r'modular/buildings/psychological_sciences.blend']:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p))
 for m in bpy.data.materials:
  if 'roof' not in m.name.lower() or not m.node_tree: continue
  r=next((n for n in m.node_tree.nodes if n.get('codex_roof_color_grain')),None)
  if r:
   print(os.path.basename(p),m.name,'range',r.color_ramp.elements[0].color[:],r.color_ramp.elements[1].color[:])
