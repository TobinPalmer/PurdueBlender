"""Lower mortar brightness/width and color-noise variation based on R14 review."""
import bpy
from pathlib import Path

root = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
blend = root / "modular" / "buildings" / "knoy_hall.blend"
bpy.ops.wm.open_mainfile(filepath=str(blend))
mat = bpy.data.materials["KNOY_Purdue_Red_Brick"]
nodes = mat.node_tree.nodes
brick = next(n for n in nodes if n.type == "TEX_BRICK")
color_mix = next(n for n in nodes if n.type == "MIX" and any(l.from_node == brick for l in mat.node_tree.links))
brick.inputs["Mortar"].default_value = (0.14, 0.12, 0.10, 1.0)
brick.inputs["Mortar Size"].default_value = 0.003
brick.inputs["Mortar Smooth"].default_value = 0.001
color_mix.inputs["Factor"].default_value = 0.04
mat["r15_material_change"] = (
    "Reduced procedural mortar brightness/width and gray-noise blend after the "
    "independent R14 review still found the joints too bright. This is a "
    "qualitative visual adjustment, not a measured masonry specification."
)
mat["r15_measurement_limit"] = (
    "Brick/mortar color and dimensions are render estimates; only the broad "
    "red-brown brick family and visible joints are supported by uncalibrated "
    "Purdue entrance photos."
)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
print("R15_SAVE", blend)
print("mortar", tuple(brick.inputs["Mortar"].default_value), brick.inputs["Mortar Size"].default_value)
print("color_noise_mix", color_mix.inputs["Factor"].default_value)
