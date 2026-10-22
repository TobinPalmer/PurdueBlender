import bpy, os, json
from pathlib import Path

ROOT = Path('.').resolve()
queue = json.loads((ROOT / 'materials/review/detailed_queue.json').read_text())
extra = [
    {"id": "dudley_hall", "file": "buildings/dudley_hall.blend", "collection": "Asset_dudley_hall"},
    {"id": "lambertus_hall", "file": "buildings/lambertus_hall.blend", "collection": "Asset_lambertus_hall"}
]
all_b = queue + extra

def build_wiley_brick_nodes(mat, color1=(0.205, 0.061, 0.029, 1.0), color2=(0.095, 0.026, 0.014, 1.0), mortar=(0.200, 0.170, 0.130, 1.0)):
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (1000, 0)
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (700, 0)
    bsdf.inputs['Roughness'].default_value = 0.60
    bsdf.inputs['IOR'].default_value = 1.50
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-1000, 0)

    geom = nodes.new('ShaderNodeNewGeometry')
    geom.location = (-1000, 300)

    sep_norm = nodes.new('ShaderNodeSeparateXYZ')
    sep_norm.location = (-800, 300)
    links.new(geom.outputs['Normal'], sep_norm.inputs['Vector'])

    math_abs = nodes.new('ShaderNodeMath')
    math_abs.operation = 'ABSOLUTE'
    math_abs.location = (-600, 300)
    links.new(sep_norm.outputs['X'], math_abs.inputs[0])

    math_gt = nodes.new('ShaderNodeMath')
    math_gt.operation = 'GREATER_THAN'
    math_gt.inputs[1].default_value = 0.5
    math_gt.location = (-400, 300)
    links.new(math_abs.outputs[0], math_gt.inputs[0])

    sep_obj = nodes.new('ShaderNodeSeparateXYZ')
    sep_obj.location = (-800, 0)
    links.new(tex_coord.outputs['Object'], sep_obj.inputs['Vector'])

    comb_yz = nodes.new('ShaderNodeCombineXYZ')
    comb_yz.location = (-600, 100)
    links.new(sep_obj.outputs['Y'], comb_yz.inputs['X'])
    links.new(sep_obj.outputs['Z'], comb_yz.inputs['Y'])

    comb_xz = nodes.new('ShaderNodeCombineXYZ')
    comb_xz.location = (-600, -100)
    links.new(sep_obj.outputs['X'], comb_xz.inputs['X'])
    links.new(sep_obj.outputs['Z'], comb_xz.inputs['Y'])

    mix_proj = nodes.new('ShaderNodeMix')
    mix_proj.data_type = 'RGBA'
    mix_proj.blend_type = 'MIX'
    mix_proj.location = (-200, 100)
    links.new(math_gt.outputs[0], mix_proj.inputs['Factor'])
    links.new(comb_xz.outputs['Vector'], mix_proj.inputs['A'])
    links.new(comb_yz.outputs['Vector'], mix_proj.inputs['B'])

    brick = nodes.new('ShaderNodeTexBrick')
    brick.location = (50, 200)
    brick.offset = 0.5
    brick.offset_frequency = 2
    brick.squash = 1.0
    brick.squash_frequency = 2
    brick.inputs['Color1'].default_value = color1
    brick.inputs['Color2'].default_value = color2
    brick.inputs['Mortar'].default_value = mortar
    brick.inputs['Scale'].default_value = 1.0
    brick.inputs['Mortar Size'].default_value = 0.006
    brick.inputs['Mortar Smooth'].default_value = 0.002
    brick.inputs['Brick Width'].default_value = 0.230
    brick.inputs['Row Height'].default_value = 0.076
    links.new(mix_proj.outputs['Result'], brick.inputs['Vector'])

    macro_noise = nodes.new('ShaderNodeTexNoise')
    macro_noise.location = (50, -100)
    macro_noise.inputs['Scale'].default_value = 3.2
    macro_noise.inputs['Detail'].default_value = 3.0
    links.new(tex_coord.outputs['Object'], macro_noise.inputs['Vector'])

    mix_color = nodes.new('ShaderNodeMix')
    mix_color.data_type = 'RGBA'
    mix_color.blend_type = 'MULTIPLY'
    mix_color.inputs['Factor'].default_value = 0.25
    mix_color.location = (350, 100)
    links.new(brick.outputs['Color'], mix_color.inputs['A'])
    links.new(macro_noise.outputs['Color'], mix_color.inputs['B'])
    links.new(mix_color.outputs['Result'], bsdf.inputs['Base Color'])

    bump_mortar = nodes.new('ShaderNodeBump')
    bump_mortar.location = (350, -100)
    bump_mortar.inputs['Strength'].default_value = 0.40
    bump_mortar.inputs['Distance'].default_value = 0.012
    links.new(brick.outputs['Fac'], bump_mortar.inputs['Height'])

    grain_noise = nodes.new('ShaderNodeTexNoise')
    grain_noise.location = (50, -350)
    grain_noise.inputs['Scale'].default_value = 160.0
    grain_noise.inputs['Detail'].default_value = 2.0
    links.new(tex_coord.outputs['Object'], grain_noise.inputs['Vector'])

    bump_grain = nodes.new('ShaderNodeBump')
    bump_grain.location = (550, -200)
    bump_grain.inputs['Strength'].default_value = 0.25
    bump_grain.inputs['Distance'].default_value = 0.002
    links.new(grain_noise.outputs['Fac'], bump_grain.inputs['Height'])
    links.new(bump_mortar.outputs['Normal'], bump_grain.inputs['Normal'])
    links.new(bump_grain.outputs['Normal'], bsdf.inputs['Normal'])
    
    mat.diffuse_color = (color1[0] * 1.5, color1[1] * 1.5, color1[2] * 1.5, 1.0)
    mat['brick_shader'] = 'wiley_triplanar_real_size_230x76mm'

def is_brick_material(name):
    n = name.lower()
    return any(k in n for k in ['brick', 'masonry', 'paver'])

results = {}

for b in all_b:
    b_id = b['id']
    fpath = ROOT / 'modular' / b['file']
    if not fpath.exists():
        continue
    bpy.ops.wm.open_mainfile(filepath=str(fpath.resolve()))
    
    upgraded_mats = []
    for m in bpy.data.materials:
        if is_brick_material(m.name):
            build_wiley_brick_nodes(m)
            upgraded_mats.append(m.name)
            
    if upgraded_mats:
        bpy.ops.wm.save_as_mainfile(filepath=str(fpath.resolve()))
        print(f"[{b_id}] Applied Wiley-style brick shader to: {upgraded_mats}")
    else:
        print(f"[{b_id}] No brick materials found.")
        
    results[b_id] = {
        'upgraded_materials': upgraded_mats
    }

(ROOT / 'scratch/wiley_brick_upgrade_report.json').write_text(json.dumps(results, indent=2))
print("All buildings updated with Wiley-style brick shader successfully!")
