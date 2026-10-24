import bpy, os
files=[r'modular/buildings/bell_tower.blend',r'modular/buildings/felix_haas_hall.blend',r'modular/buildings/psychological_sciences.blend']
for p in files:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p))
 for mat in bpy.data.materials:
  if not mat.node_tree: continue
  ns=mat.node_tree.nodes; links=mat.node_tree.links
  bump=next((n for n in ns if n.get('codex_surface_detail')),None)
  if not bump: continue
  name=mat.name.lower()
  bump.inputs['Strength'].default_value=0.06
  if 'roof' in name or 'slate' in name:
   bump.inputs['Distance'].default_value=0.0008
   for tex in ns:
    if tex.type=='TEX_NOISE' and 'Surface Detail' in tex.name:
     tex.inputs['Scale'].default_value=1.5
     tex.inputs['Detail'].default_value=1.5
  elif 'brick' in name:
   bump.inputs['Distance'].default_value=0.003
  elif any(k in name for k in ('metal','bronze','steel','aluminum','brass','copper')):
   bump.inputs['Distance'].default_value=0.001
   for tex in ns:
    if tex.type=='TEX_NOISE' and 'Surface Detail' in tex.name:
     tex.inputs['Scale'].default_value=10.0
     tex.inputs['Detail'].default_value=1.5
  else:
   bump.inputs['Distance'].default_value=0.0015
   for tex in ns:
    if tex.type=='TEX_NOISE' and 'Surface Detail' in tex.name:
     tex.inputs['Scale'].default_value=6.0
     tex.inputs['Detail'].default_value=2.0
  # Ensure all surface texture nodes are driven by explicit object-space coordinates.
  for tex in [n for n in ns if n.type in ('TEX_NOISE','TEX_BRICK') and 'Surface Detail' in n.name]:
   if tex.inputs.get('Vector') and not any(l.to_node==tex and l.to_socket==tex.inputs['Vector'] for l in links):
    tc=next((n for n in ns if n.name=='Surface Detail | Coordinates'),None)
    if tc is None: tc=ns.new('ShaderNodeTexCoord'); tc.name='Surface Detail | Coordinates'
    links.new(tc.outputs['Object'],tex.inputs['Vector'])
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(p))
 print('tuned',p)
