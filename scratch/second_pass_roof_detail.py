import bpy, os

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modular', 'buildings'))
FILES=('potter_engineering.blend','mechanical_engineering.blend','electrical_engineering.blend')

for filename in FILES:
    path=os.path.join(ROOT,filename)
    bpy.ops.wm.open_mainfile(filepath=path)
    revised=[]
    for mat in bpy.data.materials:
        if not mat.get('surface_detail') or not mat.use_nodes or not mat.node_tree:
            continue
        nt=mat.node_tree; nodes=nt.nodes; links=nt.links
        bsdf=next((n for n in nodes if n.type=='BSDF_PRINCIPLED'),None)
        if not bsdf: continue
        noise=next((n for n in nodes if n.type=='TEX_NOISE' and n.label=='Low contrast material grain'),None)
        bump=next((n for n in nodes if n.type=='BUMP' and n.label=='Fine surface relief'),None)
        if not noise or not bump: continue
        name=mat.name.lower()
        roof=('roof' in name or 'membrane' in name)
        brick=('brick' in name or 'tile' in name)
        # Meter-scale, low-amplitude relief. Existing base color stays untouched.
        noise.inputs['Scale'].default_value=3.0 if roof else (7.0 if brick else 4.0)
        noise.inputs['Detail'].default_value=1.0
        noise.inputs['Roughness'].default_value=0.45
        bump.inputs['Strength'].default_value=0.04 if roof else (0.035 if brick else 0.025)
        bump.inputs['Distance'].default_value=0.0025 if roof else (0.003 if brick else 0.0018)
        # Slight physical roughness variation on broad roof membranes only.
        if roof:
            rr=next((n for n in nodes if n.label=='Subtle roof roughness range'),None)
            if rr is None:
                rr=nodes.new('ShaderNodeMapRange'); rr.label='Subtle roof roughness range'
            rr.clamp=True
            rr.inputs['From Min'].default_value=0.0; rr.inputs['From Max'].default_value=1.0
            rr.inputs['To Min'].default_value=0.68; rr.inputs['To Max'].default_value=0.74
            links.new(noise.outputs['Fac'],rr.inputs['Value'])
            links.new(rr.outputs['Result'],bsdf.inputs['Roughness'])
        mat['surface_detail']='Meter-scaled low-contrast grain with subtle relief; original base color retained'
        revised.append(mat.name)
    bpy.ops.wm.save_as_mainfile(filepath=path)
    print('ROOF_SURFACE_PASS',filename,revised)
