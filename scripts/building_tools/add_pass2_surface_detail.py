import bpy,os
files=['south_hall','stewart_center','tarkington_hall','university_hall','walc']
for f in files:
 p=os.path.abspath(f'modular/buildings/{f}.blend'); bpy.ops.wm.open_mainfile(filepath=p)
 edited=[]
 for mat in bpy.data.materials:
  if not mat.users or not mat.node_tree: continue
  name=mat.name.lower()
  if not any(k in name for k in ('limestone','concrete','roof','membrane','slate','metal_panel')): continue
  nt=mat.node_tree; ns=nt.nodes; links=nt.links
  pr=next((n for n in ns if n.type=='BSDF_PRINCIPLED'),None)
  if not pr: continue
  roof=any(k in name for k in ('roof','membrane','slate'))
  if roof:
   strength=0.02; distance=0.00035; scale=1.0 if 'membrane' in name else 1.8; amp=0.04
  elif 'limestone' in name:
   strength=0.035; distance=0.001; scale=7.0; amp=0.025
  else:
   strength=0.035; distance=0.0008; scale=15.0; amp=0.025
  tag='PurdueMap | surface variation'
  if any(n.get('purdue_surface_variation') for n in ns): continue
  tc=next((n for n in ns if n.type=='TEX_COORD' and 'Object' in n.outputs),None)
  if tc is None: tc=ns.new('ShaderNodeTexCoord'); tc.name=tag+' | Object Coordinates'
  noise=ns.new('ShaderNodeTexNoise'); noise.name=tag+' | Meter Scale Noise'; noise.label='Object-space surface grain'; noise.inputs['Scale'].default_value=scale; noise.inputs['Detail'].default_value=1.0; noise.inputs['Roughness'].default_value=.55
  links.new(tc.outputs['Object'],noise.inputs['Vector'])
  # Color variation is low contrast and derived directly from the material's authored base color.
  base_sock=pr.inputs['Base Color']; color_ramp=None
  if not base_sock.is_linked:
   base=tuple(base_sock.default_value)
   color_ramp=ns.new('ShaderNodeValToRGB'); color_ramp.name=tag+' | Color Grain'; color_ramp.label=f'Low contrast ±{amp*100:.0f}% color grain'
   color_ramp['purdue_surface_variation']=True
   color_ramp.color_ramp.elements[0].color=tuple(max(0,c*(1-amp)) for c in base[:3])+(base[3],)
   color_ramp.color_ramp.elements[1].color=tuple(min(1,c*(1+amp)) for c in base[:3])+(base[3],)
   links.new(noise.outputs['Fac'],color_ramp.inputs['Fac']); links.new(color_ramp.outputs['Color'],base_sock)
  # Small, physically restrained roughness drift improves large surfaces under light.
  rough_sock=pr.inputs.get('Roughness')
  if rough_sock and not rough_sock.is_linked:
   rough=rough_sock.default_value
   rr=ns.new('ShaderNodeValToRGB'); rr.name=tag+' | Roughness Grain'; rr.label='Subtle roughness variation';rr['purdue_surface_variation']=True
   rr.color_ramp.elements[0].color=(max(.03,rough-.035),)*3+(1,);rr.color_ramp.elements[1].color=(min(.98,rough+.035),)*3+(1,)
   links.new(noise.outputs['Fac'],rr.inputs['Fac']);links.new(rr.outputs['Color'],rough_sock)
  # Add only when no authored normal detail exists; preserve any existing bump chain.
  normal=pr.inputs.get('Normal')
  if normal and not normal.is_linked:
   bump=ns.new('ShaderNodeBump');bump.name=tag+' | Tiny Relief';bump.label='Subtle meter-scale relief';bump.inputs['Strength'].default_value=strength;bump.inputs['Distance'].default_value=distance;bump['purdue_surface_variation']=True
   links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],normal)
  edited.append(mat.name)
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=p)
 print('UPDATED',f,edited)
