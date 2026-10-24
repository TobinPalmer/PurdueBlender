import bpy, os
ROOT=os.path.abspath('.'); ASSET=os.path.join(ROOT,'modular','buildings')
# Refine the three roof assets after visual inspection of overview and close shots.
# WALC: shared White.009 also belongs to furniture, partitions, and book spines, so copy it for roofs only.
path=os.path.join(ASSET,'walc.blend'); bpy.ops.wm.open_mainfile(filepath=path)
orig=bpy.data.materials['White.009']; roofmat=bpy.data.materials.get('WALC_Roof_Panels_White')
if roofmat is None:
 roofmat=orig.copy(); roofmat.name='WALC_Roof_Panels_White'; roofmat['roof_grain_visibility_pass']='Roof-only broad color and roughness variation; copy of White.009'
for objname in ['Atrium roof panels','Recessed roof']:
 obj=bpy.data.objects.get(objname)
 if obj and obj.material_slots: obj.material_slots[0].material=roofmat
nt=roofmat.node_tree; bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
base=tuple(bs.inputs['Base Color'].default_value)
tex=next((n for n in nt.nodes if n.type=='TEX_COORD'),None) or nt.nodes.new('ShaderNodeTexCoord')
noise=next((n for n in nt.nodes if n.type=='TEX_NOISE'),None) or nt.nodes.new('ShaderNodeTexNoise')
noise.label='Broad roof membrane grain'; noise.inputs['Scale'].default_value=.38; noise.inputs['Detail'].default_value=1.0; noise.inputs['Roughness'].default_value=.56
if not any(l.to_node==noise and l.to_socket==noise.inputs['Vector'] for l in nt.links): nt.links.new(tex.outputs['Object'],noise.inputs['Vector'])
ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.label='Roof-only low contrast variation'; ramp.color_ramp.interpolation='EASE'
ramp.color_ramp.elements[0].position=.1; ramp.color_ramp.elements[0].color=tuple(c*.94 for c in base[:3])+(1,)
ramp.color_ramp.elements[1].position=.9; ramp.color_ramp.elements[1].color=tuple(min(1,c*1.06) for c in base[:3])+(1,)
nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
for l in list(bs.inputs['Base Color'].links): nt.links.remove(l)
nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
rr=nt.nodes.new('ShaderNodeValToRGB'); rr.label='Roof-only subtle roughness drift'; rr.color_ramp.interpolation='EASE'; rr.color_ramp.elements[0].position=.12; rr.color_ramp.elements[0].color=(.74,)*3+(1,); rr.color_ramp.elements[1].position=.88; rr.color_ramp.elements[1].color=(.84,)*3+(1,)
nt.links.new(noise.outputs['Fac'],rr.inputs['Fac']); nt.links.new(rr.outputs['Color'],bs.inputs['Roughness'])
bump=nt.nodes.new('ShaderNodeBump'); bump.label='Subtle roof finish'; bump.inputs['Strength'].default_value=.02; bump.inputs['Distance'].default_value=.00015; nt.links.new(noise.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
# Softer roof tone drift on the existing slate-tile shader; the red clay hue remains authored.
bpy.ops.wm.save_as_mainfile(filepath=path); print('SAVED WALC roof-only material',roofmat.name)
# Felix: reduce the coarseness and contrast after the close-up showed overly legible blocks.
path=os.path.join(ASSET,'felix_haas_hall.blend'); bpy.ops.wm.open_mainfile(filepath=path); m=bpy.data.materials['HAAS_Slate_Roof']; nt=m.node_tree
noise=next(n for n in nt.nodes if n.type=='TEX_NOISE'); noise.inputs['Scale'].default_value=.24
cr=next(n for n in nt.nodes if n.type=='VALTORGB' and 'color variation' in n.label.lower()); bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'); base=tuple(bs.inputs['Base Color'].default_value)
cr.color_ramp.interpolation='EASE'; cr.color_ramp.elements[0].position=0; cr.color_ramp.elements[0].color=tuple(c*.055/.085 for c in cr.color_ramp.elements[0].color[:3])+(1,); cr.color_ramp.elements[1].position=1; cr.color_ramp.elements[1].color=tuple(c*1.055/1.085 for c in cr.color_ramp.elements[1].color[:3])+(1,)
# Rebuild range around the actual existing base color so the noise stays centered and hue-neutral.
cr.color_ramp.elements[0].color=tuple(c*.945 for c in base[:3])+(1,); cr.color_ramp.elements[1].color=tuple(c*1.055 for c in base[:3])+(1,)
bpy.ops.wm.save_as_mainfile(filepath=path); print('SAVED FELIX softened grain',m.name)
