import bpy
from pathlib import Path

ROOT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
ASSET = ROOT / "modular/buildings/krannert_building.blend"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))

def principled(mat):
    return next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')

stone = bpy.data.materials["KRAN_Indiana_Limestone"]
stone_bsdf = principled(stone)
stone.diffuse_color = (0.58, 0.55, 0.49, 1.0)
stone_bsdf.inputs['Base Color'].default_value = stone.diffuse_color
stone_bsdf.inputs['Roughness'].default_value = 0.78

# Add restrained, broad-scale color variation to break the near-white flat shell.
nodes, links = stone.node_tree.nodes, stone.node_tree.links
texcoord = nodes.get('R4_Stone_Object_Coordinates') or nodes.new('ShaderNodeTexCoord')
texcoord.name = 'R4_Stone_Object_Coordinates'
noise = nodes.get('R4_Stone_Subtle_Variation') or nodes.new('ShaderNodeTexNoise')
noise.name = 'R4_Stone_Subtle_Variation'
noise.inputs['Scale'].default_value = 1.7
noise.inputs['Detail'].default_value = 2.0
noise.inputs['Roughness'].default_value = 0.62
ramp = nodes.get('R4_Stone_Tone_Range') or nodes.new('ShaderNodeValToRGB')
ramp.name = 'R4_Stone_Tone_Range'
ramp.color_ramp.elements[0].position = 0.28
ramp.color_ramp.elements[0].color = (0.51, 0.49, 0.44, 1.0)
ramp.color_ramp.elements[1].position = 0.72
ramp.color_ramp.elements[1].color = (0.64, 0.61, 0.55, 1.0)
if not any(l.from_node == texcoord and l.to_node == noise for l in links):
    links.new(texcoord.outputs['Object'], noise.inputs['Vector'])
if not any(l.from_node == noise and l.to_node == ramp for l in links):
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
base_color = stone_bsdf.inputs['Base Color']
for link in list(base_color.links):
    links.remove(link)
links.new(ramp.outputs['Color'], base_color)

glass = bpy.data.materials["KRAN_Solar_Bronze_Glass"]
glass.diffuse_color = (0.025, 0.032, 0.038, 1.0)
glass_bsdf = principled(glass)
glass_bsdf.inputs['Base Color'].default_value = glass.diffuse_color
glass_bsdf.inputs['Roughness'].default_value = 0.24
glass_bsdf.inputs['Metallic'].default_value = 0.18
if 'Transmission Weight' in glass_bsdf.inputs:
    glass_bsdf.inputs['Transmission Weight'].default_value = 0.0
elif 'Transmission' in glass_bsdf.inputs:
    glass_bsdf.inputs['Transmission'].default_value = 0.0

brick = bpy.data.materials.new('KRAN_Purdue_Red_Brick_R4')
brick.diffuse_color = (0.19, 0.062, 0.043, 1.0)
brick.use_nodes = True
bn, bl = brick.node_tree.nodes, brick.node_tree.links
b = principled(brick)
b.inputs['Roughness'].default_value = 0.90
tc = bn.new('ShaderNodeTexCoord')
tc.name = 'R4_Brick_Object_Coordinates'
noise = bn.new('ShaderNodeTexNoise')
noise.name = 'R4_Nondirectional_Masonry_Variation'
noise.inputs['Scale'].default_value = 3.0
noise.inputs['Detail'].default_value = 2.0
noise.inputs['Roughness'].default_value = 0.65
ramp = bn.new('ShaderNodeValToRGB')
ramp.name = 'R4_Red_Brown_Tone_Range'
ramp.color_ramp.elements[0].position = 0.22
ramp.color_ramp.elements[0].color = (0.15, 0.048, 0.034, 1.0)
ramp.color_ramp.elements[1].position = 0.78
ramp.color_ramp.elements[1].color = (0.23, 0.078, 0.052, 1.0)
bl.new(tc.outputs['Object'], noise.inputs['Vector'])
bl.new(noise.outputs['Fac'], ramp.inputs['Fac'])
bl.new(ramp.outputs['Color'], b.inputs['Base Color'])
bump = bn.new('ShaderNodeBump')
bump.name = 'R4_Subtle_Surface_Relief'
bump.inputs['Strength'].default_value = 0.045
bump.inputs['Distance'].default_value = 0.003
bl.new(noise.outputs['Fac'], bump.inputs['Height'])
bl.new(bump.outputs['Normal'], b.inputs['Normal'])

walls = bpy.data.objects['KRAN_Exterior_Masonry_Walls']
mesh = walls.data
mesh.materials.append(brick)
brick_index = len(mesh.materials) - 1
changed = 0
for poly in mesh.polygons:
    zs = [mesh.vertices[i].co.z for i in poly.vertices]
    # Only the source-photo-visible grade-to-L1 masonry strip; avoid basement.
    if min(zs) >= -1e-5 and max(zs) <= 3.8711:
        poly.material_index = brick_index
        changed += 1
    else:
        poly.material_index = 0
walls['round4_ground_band_face_count'] = changed
walls['round4_facade_note'] = 'Ground band uses estimated red-brown masonry tone from Purdue exterior image; nondirectional variation only; coursing and scale are not measured.'
walls['round4_stone_note'] = 'Warm limestone tone and restrained procedural variation are qualitative matches to undated Purdue exterior image.'
glass['round4_facade_note'] = 'Charcoal reflective glazing approximates narrow dark windows in Purdue exterior photo; no calibrated color or dimensions claimed.'

scene = bpy.context.scene
scene['krannert_round4_facade_materials'] = 'Warm limestone, charcoal glazing, and red-brown masonry tone based on Purdue-hosted exterior photo; nondirectional variation only, qualitative.'
scene['krannert_round4_geometry_changes'] = 'No facade opening, roof, footprint, or courtyard-seam geometry changed.'
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print({'saved': str(ASSET), 'brick_faces': changed, 'wall_materials': [m.name for m in mesh.materials], 'glass': glass.name})
