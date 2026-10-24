import bpy, os
ROOT=os.path.abspath('.')
targets={
 'hovde_hall':('Hovde_Roof_Membrane',3.5),
 'hansen_life_sciences':('Roof_Membrane_Gravel',4.0),
 'knoy_hall':('KNOY_Roof_Gravel_Membrane',4.0),
}
for f,(mname,scale) in targets.items():
 p=os.path.join(ROOT,'modular','buildings',f+'.blend'); bpy.ops.wm.open_mainfile(filepath=p)
 m=bpy.data.materials[mname]; nt=m.node_tree; nodes=nt.nodes; links=nt.links
 bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
 if any(n.get('roof_color_grain_pass')=='2026_10_final' for n in nodes): raise RuntimeError(f'Already applied: {f}')
 base=bs.inputs['Base Color']
 # Preserve the full existing shader color signal, including authored procedural brick/gravel coloration.
 original=base.links[0].from_socket if base.is_linked else None
 base_value=base.default_value[:]
 tc=nodes.new('ShaderNodeTexCoord'); tc.label='Roof grain | object-space meters'
 noise=nodes.new('ShaderNodeTexNoise'); noise.label='Roof grain | subtle low-contrast variation'; noise.inputs['Scale'].default_value=scale; noise.inputs['Detail'].default_value=1.0; noise.inputs['Roughness'].default_value=.55
 remap=nodes.new('ShaderNodeMapRange'); remap.label='Roof grain | 3–5% value range'; remap.inputs['From Min'].default_value=0; remap.inputs['From Max'].default_value=1; remap.inputs['To Min'].default_value=.97; remap.inputs['To Max'].default_value=1.03
 mult=nodes.new('ShaderNodeVectorMath'); mult.operation='SCALE'; mult.label='Keep authored roof hue'
 if original:
  links.new(original,mult.inputs[0])
 else:
  mult.inputs[0].default_value=base_value[:3]
 links.new(tc.outputs['Object'],noise.inputs['Vector']); links.new(noise.outputs['Fac'],remap.inputs['Value']); links.new(remap.outputs['Result'],mult.inputs['Scale'])
 for l in list(base.links): links.remove(l)
 links.new(mult.outputs['Vector'],base)
 for n in (tc,noise,remap,mult): n['roof_color_grain_pass']='2026_10_final'
 m['roof_color_grain']='3% luminance grain at object-space 3.5–4 cycles/m; hue signal preserved; bump and geometry unchanged.'
 bpy.ops.wm.save_as_mainfile(filepath=p); print('SAVED',f,mname)
