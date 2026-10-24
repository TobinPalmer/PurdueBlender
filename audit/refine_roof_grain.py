import bpy, os
filespec={
'hicks_library':('Mat_HIKS_Roof_Gravel_Ballast',),
'lawson_hall':('LWSN_Roof_Gravel',),
'krannert_building':('KRAN_Roof_Membrane',)}
bid=os.path.splitext(os.path.basename(bpy.data.filepath))[0]
matname=filespec[bid][0];mat=bpy.data.materials[matname];nt=mat.node_tree
texcoord=next((n for n in nt.nodes if n.type=='TEX_COORD'),None)
if texcoord is None: texcoord=nt.nodes.new('ShaderNodeTexCoord')
oldnoise=next(n for n in nt.nodes if n.type=='TEX_NOISE' and n.label=='Subtle material-scale variation')
oldnoise.inputs['Scale'].default_value=24.0;oldnoise.inputs['Detail'].default_value=2.0
bump=next((n for n in nt.nodes if n.type=='BUMP' and n.label=='Fine surface relief'),None)
if bump:
    bump.inputs['Strength'].default_value=.08
    bump.inputs['Distance'].default_value=.0004
ramp=next((n for n in nt.nodes if n.type=='VALTORGB' and n.label=='Restrained tonal variation'),None)
if ramp is None: raise RuntimeError('Roof color ramp not found: '+matname)
# Keep the existing gray ramp (already set to about +/-4% around the roof base tone), but apply it at visible fine grain scale.
grain=next((n for n in nt.nodes if n.label=='Roof Grain Color Variation'),None)
if grain is None:
    grain=nt.nodes.new('ShaderNodeTexNoise');grain.label='Roof Grain Color Variation';grain.name='Roof Grain Color Variation'
grain.inputs['Scale'].default_value=7.0;grain.inputs['Detail'].default_value=1.0;grain.inputs['Roughness'].default_value=.5
nt.links.new(texcoord.outputs['Object'],grain.inputs['Vector'])
nt.links.new(grain.outputs['Fac'],ramp.inputs['Fac'])
print('UPDATED',matname,'ramp',[(round(e.position,3),tuple(round(c,4) for c in e.color[:3])) for e in ramp.color_ramp.elements], 'color grain scale',grain.inputs['Scale'].default_value,'bump', (bump.inputs['Strength'].default_value,bump.inputs['Distance'].default_value) if bump else None)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
