import bpy,os
files=[r'modular/buildings/bell_tower.blend',r'modular/buildings/felix_haas_hall.blend',r'modular/buildings/psychological_sciences.blend']
for p in files:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p))
 for mat in bpy.data.materials:
  if 'roof' not in mat.name.lower() or not mat.node_tree: continue
  nt=mat.node_tree; ns=nt.nodes; links=nt.links
  pr=next((n for n in ns if n.type=='BSDF_PRINCIPLED'),None)
  if not pr: continue
  base=tuple(pr.inputs['Base Color'].default_value)
  if pr.inputs['Base Color'].is_linked: continue
  noise=next((n for n in ns if n.type=='TEX_NOISE' and 'Surface Detail' in n.name),None)
  tc=next((n for n in ns if n.type=='TEX_COORD' and 'Surface Detail' in n.name),None)
  if not noise:
   noise=ns.new('ShaderNodeTexNoise'); noise.name='Roof Color Grain | Noise'; noise.inputs['Scale'].default_value=2.5; noise.inputs['Detail'].default_value=1.0; noise.inputs['Roughness'].default_value=0.55
  else:
   noise.name='Roof Color Grain | Noise'; noise.inputs['Detail'].default_value=1.0
   noise.inputs['Scale'].default_value=2.6 if 'slate' in mat.name.lower() else (1.8 if 'membrane' in mat.name.lower() else 2.3)
  if not tc:
   tc=ns.new('ShaderNodeTexCoord'); tc.name='Surface Detail | Coordinates'
  if not any(l.to_node==noise and l.to_socket==noise.inputs['Vector'] for l in links): links.new(tc.outputs['Object'],noise.inputs['Vector'])
  ramp=next((n for n in ns if n.get('codex_roof_color_grain')),None)
  if not ramp:
   ramp=ns.new('ShaderNodeValToRGB'); ramp.name='Roof Color Grain | 4 percent'; ramp.label='Low contrast roof color variation (±4%)'; ramp['codex_roof_color_grain']=True
  ramp.color_ramp.elements[0].position=0.0; ramp.color_ramp.elements[0].color=tuple(min(1.0,c*0.96) for c in base[:3])+(base[3],)
  ramp.color_ramp.elements[1].position=1.0; ramp.color_ramp.elements[1].color=tuple(min(1.0,c*1.04) for c in base[:3])+(base[3],)
  links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
  links.new(ramp.outputs['Color'],pr.inputs['Base Color'])
  # Keep tactile relief subordinate to the visible color grain.
  bump=next((n for n in ns if n.get('codex_surface_detail')),None)
  if bump:
   bump.inputs['Strength'].default_value=0.025
   bump.inputs['Distance'].default_value=0.00025
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(p))
 print('added low contrast roof grain',os.path.basename(p))
