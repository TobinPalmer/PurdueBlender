import bpy,os
ROOT=os.path.abspath('.')
settings={
 'hovde_hall':('Hovde_Roof_Membrane',3.0,0.76,0.82),
 'hansen_life_sciences':('Roof_Membrane_Gravel',4.0,0.77,0.85),
 'knoy_hall':('KNOY_Roof_Gravel_Membrane',4.0,0.77,0.85),
}
for f,(matname,scale,rmin,rmax) in settings.items():
 path=os.path.join(ROOT,'modular','buildings',f+'.blend'); bpy.ops.wm.open_mainfile(filepath=path)
 m=bpy.data.materials[matname]; nt=m.node_tree; ns=nt.nodes; ls=nt.links
 bs=next(n for n in ns if n.type=='BSDF_PRINCIPLED')
 if any(n.get('roof_detail_pass')=='2026_10' for n in ns): raise RuntimeError('roof pass already exists')
 tc=ns.new('ShaderNodeTexCoord'); tc.label='Roof detail | object coordinates'
 noise=ns.new('ShaderNodeTexNoise'); noise.label='Roof membrane | subtle aggregate variation'; noise.inputs['Scale'].default_value=scale; noise.inputs['Detail'].default_value=1.0; noise.inputs['Roughness'].default_value=0.55
 remap=ns.new('ShaderNodeMapRange'); remap.label='Roof membrane | restrained roughness range'; remap.inputs['From Min'].default_value=0; remap.inputs['From Max'].default_value=1; remap.inputs['To Min'].default_value=rmin; remap.inputs['To Max'].default_value=rmax
 ls.new(tc.outputs['Object'],noise.inputs['Vector']); ls.new(noise.outputs['Fac'],remap.inputs['Value'])
 # Roughness is the only shader channel changed: keep the authored roof color and relief network intact.
 for link in list(bs.inputs['Roughness'].links): ls.remove(link)
 ls.new(remap.outputs['Result'],bs.inputs['Roughness'])
 for n in (tc,noise,remap): n['roof_detail_pass']='2026_10'
 m['roof_surface_detail']='Object-space, meter-scale variation in roughness only; authored roof color and bump relief preserved.'
 bpy.ops.wm.save_as_mainfile(filepath=path); print('SAVED',f,matname)
