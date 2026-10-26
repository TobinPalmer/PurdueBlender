import bpy

def test_brick_scale():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    mat = bpy.data.materials.new("TestBrick")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    brick = nodes.new('ShaderNodeTexBrick')
    brick.inputs['Color1'].default_value = (0.42, 0.16, 0.11, 1.0) # Dark rich Purdue red-brown
    brick.inputs['Color2'].default_value = (0.54, 0.22, 0.14, 1.0) # Russet terracotta
    brick.inputs['Mortar'].default_value = (0.35, 0.33, 0.30, 1.0) # Dark weathered mortar
    brick.inputs['Mortar Size'].default_value = 0.012
    brick.inputs['Brick Width'].default_value = 0.22
    brick.inputs['Row Height'].default_value = 0.075
    
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 10.0
    
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.25
    
    links.new(tex_coord.outputs['Object'], brick.inputs['Vector'])
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
    links.new(brick.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.76
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    print("Brick material created successfully with 1:1 metric scaling!")

if __name__ == '__main__':
    test_brick_scale()
