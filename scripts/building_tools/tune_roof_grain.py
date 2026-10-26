import bpy,os
configs={r'modular/buildings/bell_tower.blend':(0.05,1.3),r'modular/buildings/felix_haas_hall.blend':(0.03,0.65),r'modular/buildings/psychological_sciences.blend':(0.04,1.15)}
for p,(amt,scale) in configs.items():
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p))
 for m in bpy.data.materials:
  if 'roof' not in m.name.lower() or not m.node_tree: continue
  pr=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  ramp=next((n for n in m.node_tree.nodes if n.get('codex_roof_color_grain')),None)
  noise=next((n for n in m.node_tree.nodes if n.name=='Roof Color Grain | Noise'),None)
  if not pr or not ramp or not noise: continue
  base=pr.inputs['Base Color'].default_value[:]
  # Recover authored base through the midpoint of current ramp, preserving the material's color.
  c0=ramp.color_ramp.elements[0].color; c1=ramp.color_ramp.elements[1].color
  base=tuple((c0[i]+c1[i])*0.5 for i in range(4))
  ramp.color_ramp.elements[0].color=tuple(base[i]*(1-amt) for i in range(3))+(base[3],)
  ramp.color_ramp.elements[1].color=tuple(min(1.0,base[i]*(1+amt)) for i in range(3))+(base[3],)
  noise.inputs['Scale'].default_value=scale
  noise.inputs['Detail'].default_value=0.8
  bump=next((n for n in m.node_tree.nodes if n.get('codex_surface_detail')),None)
  if bump: bump.inputs['Strength'].default_value=0.012; bump.inputs['Distance'].default_value=0.00012
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(p))
 print('adjusted color grain',os.path.basename(p),amt,scale)
