import bpy

# Test creating the Wiley-style brick shader on a test material
mat = bpy.data.materials.new(name="Test_Wiley_Brick")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

out = nodes.new('ShaderNodeOutputMaterial')
out.location = (1000, 0)
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.location = (700, 0)
bsdf.inputs['Roughness'].default_value = 0.60
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
brick.inputs['Color1'].default_value = (0.24, 0.08, 0.04, 1.0) # warm russet
brick.inputs['Color2'].default_value = (0.13, 0.04, 0.02, 1.0) # darker accent
brick.inputs['Mortar'].default_value = (0.22, 0.19, 0.15, 1.0) # mortar joint
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

print("Successfully built Wiley-style brick shader with", len(nodes), "nodes and", len(links), "links.")
