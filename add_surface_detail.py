import bpy, os
files = [
    r'modular/buildings/bell_tower.blend',
    r'modular/buildings/felix_haas_hall.blend',
    r'modular/buildings/psychological_sciences.blend',
]
for path in files:
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(path))
    changed=[]
    for mat in bpy.data.materials:
        if not mat.use_nodes or mat.node_tree is None: continue
        nodes=mat.node_tree.nodes
        principled=next((n for n in nodes if n.type=='BSDF_PRINCIPLED'),None)
        if not principled: continue
        name=mat.name.lower()
        if any(k in name for k in ('label','ink','emissive','screen','wayfinding','preview')): continue
        if any(n.type=='BUMP' and n.get('codex_surface_detail') for n in nodes): continue
        # Semantically appropriate surface scale and relief. Keep original color and geometry.
        if 'brick' in name:
            tex=nodes.new('ShaderNodeTexBrick'); tex.name='Surface Detail | Masonry'; tex.label='Subtle masonry joint relief'
            tex.inputs['Scale'].default_value=1.0
            tex.inputs['Mortar Size'].default_value=0.025
            tex.inputs['Mortar Smooth'].default_value=0.08
            tex.inputs['Brick Width'].default_value=0.55
            tex.inputs['Row Height'].default_value=0.18
            height_output=tex.outputs['Color']
            dist=0.012
        elif any(k in name for k in ('limestone','concrete','terrazzo','plaster','painted','porcelain','slate','roof','oak','wood','hardwood','rug','upholstery','carpet','leather','laminate','resilient')):
            tex=nodes.new('ShaderNodeTexNoise'); tex.name='Surface Detail | Fine Relief'; tex.label='Fine material grain'
            tex.inputs['Scale'].default_value=22.0 if any(k in name for k in ('limestone','concrete','plaster','painted','porcelain','terrazzo')) else 9.0
            tex.inputs['Detail'].default_value=3.0
            tex.inputs['Roughness'].default_value=0.68
            height_output=tex.outputs['Fac']
            dist=0.008 if any(k in name for k in ('limestone','concrete','plaster','painted','porcelain','terrazzo')) else 0.012
        elif any(k in name for k in ('bronze','metal','steel','aluminum','brass','copper','membrane')):
            tex=nodes.new('ShaderNodeTexNoise'); tex.name='Surface Detail | Metal Grain'; tex.label='Fine metal surface variation'
            tex.inputs['Scale'].default_value=32.0
            tex.inputs['Detail'].default_value=2.0
            height_output=tex.outputs['Fac']
            dist=0.003
        else:
            continue
        tc=nodes.new('ShaderNodeTexCoord'); tc.name='Surface Detail | Coordinates'
        bump=nodes.new('ShaderNodeBump'); bump.name='Surface Detail | Relief'; bump.label='Subtle real-scale relief'
        bump.inputs['Strength'].default_value=0.16
        bump.inputs['Distance'].default_value=dist
        bump['codex_surface_detail']=True
        links=mat.node_tree.links
        links.new(tc.outputs['Object'],tex.inputs['Vector'])
        links.new(height_output,bump.inputs['Height'])
        links.new(bump.outputs['Normal'],principled.inputs['Normal'])
        rough=principled.inputs.get('Roughness')
        if rough and any(k in name for k in ('limestone','concrete','plaster','painted','brick','terrazzo')):
            rough.default_value=max(rough.default_value,0.72)
        changed.append(mat.name)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(path))
    print('UPDATED',path,changed)
