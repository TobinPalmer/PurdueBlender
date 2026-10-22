import bpy

def test_shaders():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # Brick Shader with Procedural Brick Texture
    mat_brick = bpy.data.materials.new("Purdue_Red_Brick")
    mat_brick.use_nodes = True
    nodes = mat_brick.node_tree.nodes
    links = mat_brick.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (5.0, 5.0, 5.0)
    
    brick = nodes.new('ShaderNodeTexBrick')
    brick.inputs['Color1'].default_value = (0.42, 0.16, 0.10, 1.0) # Dark red
    brick.inputs['Color2'].default_value = (0.55, 0.22, 0.14, 1.0) # Russet orange-red
    brick.inputs['Mortar'].default_value = (0.60, 0.58, 0.55, 1.0) # Mortar grey
    brick.inputs['Mortar Size'].default_value = 0.015
    brick.inputs['Mortar Smooth'].default_value = 0.1
    brick.inputs['Brick Width'].default_value = 0.22
    brick.inputs['Row Height'].default_value = 0.08
    
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 25.0
    
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.15
    
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], brick.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    
    links.new(brick.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.78
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    print("Shader test passed!")

if __name__ == '__main__':
    test_shaders()
