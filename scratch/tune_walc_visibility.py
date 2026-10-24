import bpy,os
p=os.path.abspath('modular/buildings/walc.blend'); bpy.ops.wm.open_mainfile(filepath=p)
for name,amp,scale in [('Roof.009',.12,.24),('WALC_Reference_Roof',.12,.24),('WALC_Roof_Panels_White',.09,.26)]:
 m=bpy.data.materials[name]; nt=m.node_tree
 noise=next(n for n in nt.nodes if n.type=='TEX_NOISE'); noise.inputs['Scale'].default_value=scale
 bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'); base=tuple(bs.inputs['Base Color'].default_value)
 cr=next(n for n in nt.nodes if n.type=='VALTORGB' and ('color grain' in n.label.lower() or 'contrast variation' in n.label.lower()))
 cr.color_ramp.interpolation='EASE'; cr.color_ramp.elements[0].position=.08; cr.color_ramp.elements[1].position=.92
 cr.color_ramp.elements[0].color=tuple(c*(1-amp) for c in base[:3])+(1,)
 cr.color_ramp.elements[1].color=tuple(min(1,c*(1+amp)) for c in base[:3])+(1,)
 rr=next((n for n in nt.nodes if n.type=='VALTORGB' and 'roughness' in n.label.lower()),None)
 if rr:
  bs.inputs['Roughness'].links[0].from_node # ensure connection exists
  rr.color_ramp.interpolation='EASE'; rr.color_ramp.elements[0].position=.1; rr.color_ramp.elements[1].position=.9
  base_rough=.8 if name!='WALC_Roof_Panels_White' else .8
  rr.color_ramp.elements[0].color=(.71 if name!='WALC_Roof_Panels_White' else .73,)*3+(1,)
  rr.color_ramp.elements[1].color=(.88 if name!='WALC_Roof_Panels_White' else .87,)*3+(1,)
 print('TUNED',name,'scale',scale,'contrast',amp)
bpy.ops.wm.save_as_mainfile(filepath=p); print('SAVED',p)
