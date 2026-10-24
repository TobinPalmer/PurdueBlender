import bpy, os

ROOT=r'C:\Users\Tobin\Documents\Blender\PurdueMap'
BUILD=os.path.join(ROOT,'modular','buildings')
REPORT=os.path.join(ROOT,'audit','texture_batch_1')

def find_principled(mat):
    return next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)

def coord_node(mat):
    nt=mat.node_tree
    tc=next((n for n in nt.nodes if n.type=='TEX_COORD'),None)
    if tc is None:
        tc=nt.nodes.new('ShaderNodeTexCoord'); tc.location=(-900,150)
    return tc

def ensure_object_inputs(mat):
    nt=mat.node_tree; tc=coord_node(mat)
    for n in nt.nodes:
        if n.type in {'TEX_NOISE','TEX_BRICK','TEX_VORONOI','TEX_WAVE'}:
            sock=n.inputs.get('Vector')
            if sock and not any(l.to_socket==sock for l in nt.links):
                nt.links.new(tc.outputs['Object'],sock)

def add_surface_detail(mat, scale, bump_distance, strength, roughness=None, title='Subtle meter-scale surface grain'):
    nt=mat.node_tree; p=find_principled(mat)
    if not p: return 'skipped: no Principled shader'
    ensure_object_inputs(mat)
    # Chain a quiet, scale-appropriate noise bump into the existing normal chain.
    old=next((l.from_socket for l in nt.links if l.to_socket==p.inputs['Normal']),None)
    tc=coord_node(mat)
    noise=nt.nodes.new('ShaderNodeTexNoise'); noise.name=title+' Noise'; noise.label=title
    noise.inputs['Scale'].default_value=scale; noise.inputs['Detail'].default_value=2.0; noise.inputs['Roughness'].default_value=0.55
    noise.location=(-620,-360)
    nt.links.new(tc.outputs['Object'],noise.inputs['Vector'])
    bump=nt.nodes.new('ShaderNodeBump'); bump.name=title+' Bump'; bump.label=title
    bump.inputs['Strength'].default_value=strength; bump.inputs['Distance'].default_value=bump_distance
    bump.location=(-280,-300)
    if old: nt.links.remove(next(l for l in nt.links if l.to_socket==p.inputs['Normal']))
    nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
    if old: nt.links.new(old,bump.inputs['Normal'])
    nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
    # Softly vary roughness by no more than 0.04, preserving the material's authored response.
    if roughness is not None:
        rr=p.inputs['Roughness']; prior=next((l.from_socket for l in nt.links if l.to_socket==rr),None)
        if prior is None:
            base=float(rr.default_value); rr.default_value=base
            ramp=nt.nodes.new('ShaderNodeMapRange'); ramp.name=title+' Roughness'; ramp.label='Subtle roughness variation'
            ramp.inputs['From Min'].default_value=0.0; ramp.inputs['From Max'].default_value=1.0
            ramp.inputs['To Min'].default_value=max(0.0,base-roughness); ramp.inputs['To Max'].default_value=min(1.0,base+roughness)
            ramp.location=(-300,-600); nt.links.new(noise.outputs['Fac'],ramp.inputs['Value']); nt.links.new(ramp.outputs['Result'],rr)
    return f'added Object-space grain scale={scale}/m bump={bump_distance}m strength={strength}'

def soften_named_bumps(mat, bump_strength, bump_distance):
    changed=[]
    for n in mat.node_tree.nodes:
        if n.type=='BUMP':
            n.inputs['Strength'].default_value=bump_strength
            n.inputs['Distance'].default_value=bump_distance
            changed.append(n.name)
    return changed

def get_mat(name): return bpy.data.materials.get(name)

records=[]
for building in ['armory','beering_hall','american_railway_building','brown_laboratory_of_chemistry','peirce_hall']:
    path=os.path.join(BUILD,building+'.blend')
    bpy.ops.wm.open_mainfile(filepath=path)
    changes=[]
    if building=='armory':
        # Existing brick courses are dimensioned correctly; reduce the relief to masonry-scale.
        m=get_mat('Purdue_Red_Brick')
        if m:
            for n in m.node_tree.nodes:
                if n.type=='BUMP':
                    if n.name=='Bump': n.inputs['Strength'].default_value=0.16; n.inputs['Distance'].default_value=0.0022
                    elif n.name=='Bump.001': n.inputs['Strength'].default_value=0.1; n.inputs['Distance'].default_value=0.00045
            ensure_object_inputs(m); changes.append('Purdue_Red_Brick: retained true-size ~230x76mm bond; toned down deep relief')
        # Limestone, copper and granite already have mapped authored procedural detail.
        for n in ['Bedford_Indiana_Limestone','Armory_Roof_Copper','Armory_Barre_Granite']:
            if get_mat(n): changes.append(n+': retained existing mapped surface chain')
    elif building=='beering_hall':
        for name in ['Beering_Purdue_Red_Brick','Beering_Plaza_Brick_Pavers']:
            m=get_mat(name)
            if m:
                for n in m.node_tree.nodes:
                    if n.type=='BUMP':
                        n.inputs['Strength'].default_value=0.16 if n.name=='Bump' else 0.1
                        n.inputs['Distance'].default_value=0.0022 if n.name=='Bump' else 0.00045
                ensure_object_inputs(m); changes.append(name+': preserved 230x76mm coursing; softened exaggerated relief')
        for name in ['Beering_Architectural_Bronze_Metal','Beering_Bedford_Limestone','Beering_Verdigris_Copper_Dome']:
            m=get_mat(name)
            if m:
                ensure_object_inputs(m); changes.append(name+': retained authored Object-space grain and roughness variation')
    elif building=='american_railway_building':
        for name,scale,bump,strength,rvar in [
            ('RAIL | warm muted limestone trim',8,0.0008,0.13,0.035),
            ('RAIL | sealed warm concrete',4,0.0014,0.12,0.03),
            ('RAIL | warm off-white plaster',4,0.0008,0.1,0.025),
            ('RAIL | dark charcoal membrane and metal',22,0.00035,0.1,0.02),
            ('RAIL | dark bronze window frames',30,0.0002,0.08,0.025),
        ]:
            m=get_mat(name)
            if m: changes.append(name+': '+add_surface_detail(m,scale,bump,strength,rvar,'Architectural microtexture'))
        m=get_mat('RAIL | warm red running-bond brick')
        if m:
            ensure_object_inputs(m)
            for n in m.node_tree.nodes:
                if n.type=='BUMP': n.inputs['Strength'].default_value=0.09; n.inputs['Distance'].default_value=0.0015
            changes.append('RAIL brick: retained existing bond/relief and repaired missing coordinate inputs')
    elif building=='brown_laboratory_of_chemistry':
        # Existing brick pattern has full-size brick dimensions. Keep its color and masonry rhythm.
        for name in ['BRWN | running-bond brick on east-west elevations','BRWN | running-bond brick on north-south elevations']:
            m=get_mat(name)
            if m:
                ensure_object_inputs(m)
                for n in m.node_tree.nodes:
                    if n.type=='BUMP': n.inputs['Strength'].default_value=0.14; n.inputs['Distance'].default_value=0.002
                changes.append(name+': connected true-scale Object coordinates and reduced mortar relief')
        m=get_mat('BRWN | pale cast concrete')
        if m:
            ensure_object_inputs(m)
            for n in m.node_tree.nodes:
                if n.type=='BUMP': n.inputs['Strength'].default_value=0.1; n.inputs['Distance'].default_value=0.0015
            changes.append('BRWN concrete: repaired missing Object-space vector; subtle aggregate variation')
        for name,scale,bump,strength,rvar in [
            ('BRWN | dark bronze window frames',28,0.00025,0.08,0.02),
            ('BRWN | lab resilient flooring',12,0.00025,0.08,0.025),
            ('BRWN | corridor terrazzo',18,0.0003,0.08,0.025),
        ]:
            m=get_mat(name)
            if m: changes.append(name+': '+add_surface_detail(m,scale,bump,strength,rvar,'Architectural microtexture'))
    elif building=='peirce_hall':
        m=get_mat('Peirce | fired red brick and pale mortar')
        if m:
            ensure_object_inputs(m)
            for n in m.node_tree.nodes:
                if n.type=='TEX_BRICK':
                    n.inputs['Brick Width'].default_value=0.24; n.inputs['Row Height'].default_value=0.076
                    n.inputs['Mortar Size'].default_value=0.009; n.inputs['Mortar Smooth'].default_value=0.003
                if n.type=='BUMP': n.inputs['Strength'].default_value=0.14; n.inputs['Distance'].default_value=0.0018
            changes.append('Peirce fired brick: corrected true-scale running bond to 240x76mm; softened relief')
        m=get_mat('Peirce | weathered pale gray roof membrane')
        if m:
            ensure_object_inputs(m)
            changes.append('Peirce roof membrane: connected existing noise to Object-space mapping')
            changes.append('Peirce roof: '+add_surface_detail(m,22,0.00045,0.1,0.02,'Fine roof membrane grain'))
        m=get_mat('Peirce | warm buff limestone and precast')
        if m: changes.append('Peirce limestone: '+add_surface_detail(m,6,0.0009,0.1,0.035,'Bedford limestone grain'))
    bpy.ops.wm.save_as_mainfile(filepath=path)
    records.append((building,changes))

with open(os.path.join(REPORT,'texture_changes.md'),'w',encoding='utf-8') as f:
    f.write('# Texture pass: five building assets\n\n')
    for building, changes in records:
        f.write('## '+building.replace('_',' ').title()+'\n\n')
        for line in changes: f.write('- '+line+'\n')
        f.write('\n')
print('SAVED',len(records),'building blends')
