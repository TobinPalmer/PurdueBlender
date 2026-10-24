import bpy, os
spec={
 'hicks_library': {'Mat_HIKS_Roof_Gravel_Ballast':(.68,.84,.55),'Mat_HIKS_Site_Lawn':(.88,.98,.75),'Mat_HIKS_Plaza_Paver_Concrete':(.56,.68,.65)},
 'lawson_hall': {'LWSN_Roof_Gravel':(.68,.84,.55),'LWSN_Site_Lawn':(.88,.98,.75),'LWSN_Plaza_Pavers':(.56,.68,.65)},
 'krannert_building': {'KRAN_Roof_Membrane':(.70,.84,.55),'KRAN_Plaza_Paving':(.72,.84,.65)},
}
for matname,(lo,hi,scale) in spec[os.path.splitext(os.path.basename(bpy.data.filepath))[0]].items():
    mat=bpy.data.materials.get(matname)
    if not mat or not mat.node_tree:
        print('SKIP missing material',matname); continue
    nt=mat.node_tree; principled=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if not principled: print('SKIP missing shader',matname); continue
    prev=next((l for l in nt.links if l.to_node==principled and l.to_socket.name=='Roughness'),None)
    base=principled.inputs['Roughness'].default_value if not prev else .8
    if prev: nt.links.remove(prev)
    texcoord=next((n for n in nt.nodes if n.type=='TEX_COORD'),None)
    if not texcoord: texcoord=nt.nodes.new('ShaderNodeTexCoord')
    noise=next((n for n in nt.nodes if n.label=='Broad Roughness Variation'),None)
    if not noise:
        noise=nt.nodes.new('ShaderNodeTexNoise');noise.label='Broad Roughness Variation';noise.name='Broad Roughness Variation'
    noise.inputs['Scale'].default_value=scale; noise.inputs['Detail'].default_value=1.0; noise.inputs['Roughness'].default_value=.5
    remap=next((n for n in nt.nodes if n.label=='Restrained Surface Roughness'),None)
    if not remap:
        remap=nt.nodes.new('ShaderNodeMapRange');remap.label='Restrained Surface Roughness';remap.name='Restrained Surface Roughness'
    remap.clamp=True
    remap.inputs['From Min'].default_value=0;remap.inputs['From Max'].default_value=1
    remap.inputs['To Min'].default_value=lo;remap.inputs['To Max'].default_value=hi
    nt.links.new(texcoord.outputs['Object'],noise.inputs['Vector'])
    nt.links.new(noise.outputs['Fac'],remap.inputs['Value'])
    nt.links.new(remap.outputs['Result'],principled.inputs['Roughness'])
    mat['roughness_variation']='Broad object-space noise mapped to restrained roughness range; base color unchanged'
    print('UPDATED',matname,'roughness range',lo,hi,'scale',scale,'prior',base)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
