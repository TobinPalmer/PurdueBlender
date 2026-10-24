import bpy

ASSET = r"modular/buildings/life_science_plant_and_soils_laboratory.blend"
bpy.ops.wm.open_mainfile(filepath=ASSET)

def node(mat, node_type):
    return next(n for n in mat.node_tree.nodes if n.type == node_type)

brick = bpy.data.materials["LSPS | mottled Purdue red-brown brick"]
nt = brick.node_tree
bsdf = node(brick, "BSDF_PRINCIPLED")
texcoord = node(brick, "TEX_COORD")
ramp = node(brick, "VALTORGB")
geometry = nt.nodes.new("ShaderNodeNewGeometry")
geometry.label = "World-space facade basis for consistent running-bond courses"
position = nt.nodes.new("ShaderNodeSeparateXYZ")
nt.links.new(geometry.outputs["Position"], position.inputs[0])
normal = nt.nodes.new("ShaderNodeSeparateXYZ")
nt.links.new(geometry.outputs["Normal"], normal.inputs[0])
abs_x = nt.nodes.new("ShaderNodeMath")
abs_x.operation = "ABSOLUTE"
nt.links.new(normal.outputs["X"], abs_x.inputs[0])
axes = []
for name, axis in (("LSPS | brick courses on XZ faces", "X"), ("LSPS | brick courses on YZ faces", "Y")):
    combine = nt.nodes.new("ShaderNodeCombineXYZ")
    combine.label = name + " coordinate projection"
    nt.links.new(position.outputs[axis], combine.inputs["X"])
    nt.links.new(position.outputs["Z"], combine.inputs["Y"])
    tex = nt.nodes.new("ShaderNodeTexBrick")
    tex.label = name
    tex.inputs["Scale"].default_value = 2.0
    tex.inputs["Color1"].default_value = (0.34, 0.105, 0.065, 1.0)
    tex.inputs["Color2"].default_value = (0.44, 0.165, 0.105, 1.0)
    tex.inputs["Mortar"].default_value = (0.59, 0.54, 0.46, 1.0)
    tex.inputs["Brick Width"].default_value = 0.42
    tex.inputs["Row Height"].default_value = 0.13
    tex.inputs["Mortar Size"].default_value = 0.018
    tex.inputs["Mortar Smooth"].default_value = 0.08
    nt.links.new(combine.outputs["Vector"], tex.inputs["Vector"])
    axes.append(tex)
projection_mix = nt.nodes.new("ShaderNodeMixRGB")
projection_mix.label = "Select running bond by facade orientation"
nt.links.new(abs_x.outputs[0], projection_mix.inputs[0])
nt.links.new(axes[0].outputs["Color"], projection_mix.inputs[1])
nt.links.new(axes[1].outputs["Color"], projection_mix.inputs[2])
detail_mix = nt.nodes.new("ShaderNodeMixRGB")
detail_mix.label = "Brick faces with subtle clay variation"
detail_mix.inputs[0].default_value = 0.20
nt.links.new(projection_mix.outputs["Color"], detail_mix.inputs[1])
nt.links.new(ramp.outputs["Color"], detail_mix.inputs[2])
nt.links.new(detail_mix.outputs["Color"], bsdf.inputs["Base Color"])

glass = bpy.data.materials["LSPS | schematic clear facade glazing"]
glass_bsdf = node(glass, "BSDF_PRINCIPLED")
glass_bsdf.inputs["Base Color"].default_value = (0.105, 0.15, 0.16, 1.0)
glass_bsdf.inputs["Metallic"].default_value = 0.22
glass_bsdf.inputs["Roughness"].default_value = 0.26
glass_mix = node(glass, "MIX_SHADER")
glass_mix.inputs[0].default_value = 0.78

greenhouse = bpy.data.materials["LSPS | greenhouse clear glazing"]
greenhouse_bsdf = node(greenhouse, "BSDF_PRINCIPLED")
greenhouse_bsdf.inputs["Base Color"].default_value = (0.48, 0.53, 0.51, 1.0)
greenhouse_bsdf.inputs["Metallic"].default_value = 0.17
greenhouse_bsdf.inputs["Roughness"].default_value = 0.29
greenhouse_mix = node(greenhouse, "MIX_SHADER")
greenhouse_mix.inputs[0].default_value = 0.62

brick["r2_source_basis"] = "2019 Google Street View, 135 S Russell Dr: visible running-bond red-brown masonry"
glass["r2_source_basis"] = "2019 Google Street View, 135 S Russell Dr: darker reflective window glazing in light masonry frames"
greenhouse["r2_source_basis"] = "2019 Google Street View, 135 S Russell Dr: adjoining large gray glazed/panel volume with vertical glazed bay"
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print("Saved R2 material refinements", ASSET)
