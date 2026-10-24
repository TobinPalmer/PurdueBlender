import bpy
from pathlib import Path

ROOT = Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
ASSET = ROOT / 'modular/buildings/krannert_building.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))

mat = bpy.data.materials['KRAN_Purdue_Red_Brick_R4']
mat.diffuse_color = (0.19, 0.062, 0.043, 1.0)
nodes, links = mat.node_tree.nodes, mat.node_tree.links
bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
for link in list(bsdf.inputs['Base Color'].links):
    links.remove(link)
for link in list(bsdf.inputs['Normal'].links):
    links.remove(link)
for node in list(nodes):
    if node != bsdf and node.type not in {'OUTPUT_MATERIAL'}:
        nodes.remove(node)

tc = nodes.new('ShaderNodeTexCoord')
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 3.0
noise.inputs['Detail'].default_value = 2.0
noise.inputs['Roughness'].default_value = 0.65
ramp = nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = 0.22
ramp.color_ramp.elements[0].color = (0.15, 0.048, 0.034, 1.0)
ramp.color_ramp.elements[1].position = 0.78
ramp.color_ramp.elements[1].color = (0.23, 0.078, 0.052, 1.0)
bump = nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = 0.045
bump.inputs['Distance'].default_value = 0.003
links.new(tc.outputs['Object'], noise.inputs['Vector'])
links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
links.new(noise.outputs['Fac'], bump.inputs['Height'])
links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
bsdf.inputs['Roughness'].default_value = 0.90
mat['round4_note'] = ('Dark red-brown ground band based on undated Purdue exterior photo. '
                       'Non-directional color variation only; brick coursing and scale are not modeled or verified.')
bpy.data.scenes[0]['krannert_round4_brick_pattern_limit'] = 'No coursing is claimed; source image does not resolve brick joints or module dimensions.'
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('Saved non-directional R4 masonry tone; no mesh geometry changed.')
