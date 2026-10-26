import bpy,os
files=[r'modular/buildings/bell_tower.blend',r'modular/buildings/felix_haas_hall.blend',r'modular/buildings/psychological_sciences.blend']
for p in files:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p))
 for mat in bpy.data.materials:
  if not mat.node_tree or 'roof' not in mat.name.lower(): continue
  bump=next((n for n in mat.node_tree.nodes if n.get('codex_surface_detail')),None)
  if bump:
   bump.inputs['Strength'].default_value=0.025 if 'slate' in mat.name.lower() else 0.035
   bump.inputs['Distance'].default_value=0.00035 if 'slate' in mat.name.lower() else 0.0005
  for n in mat.node_tree.nodes:
   if n.type=='TEX_NOISE' and 'Surface Detail' in n.name:
    n.inputs['Scale'].default_value=2.0 if 'slate' in mat.name.lower() else 3.0
    n.inputs['Detail'].default_value=1.5
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(p))
 print('roof softened',os.path.basename(p))
