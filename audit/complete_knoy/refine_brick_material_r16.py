"""Apply the modest photo-led Knoy brick/mortar material revision R16."""
import bpy
from pathlib import Path

ROOT = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
BLEND = ROOT / "modular" / "buildings" / "knoy_hall.blend"
OUT = ROOT / "audit" / "complete_knoy" / "knoy_hall_r16_candidate.blend"
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
mat = bpy.data.materials["KNOY_Purdue_Red_Brick"]
brick = next(n for n in mat.node_tree.nodes if n.type == "TEX_BRICK")
brick.inputs["Color1"].default_value = (0.120, 0.032, 0.013, 1.0)
brick.inputs["Color2"].default_value = (0.055, 0.013, 0.005, 1.0)
brick.inputs["Mortar"].default_value = (0.10, 0.08, 0.06, 1.0)
brick.inputs["Mortar Size"].default_value = 0.002
mat["r16_material_change"] = (
    "Slightly deepened the red-brown brick palette and reduced mortar brightness "
    "and apparent width after review against Purdue's qualitative entrance photos. "
    "This is a visual estimate, not a measured material specification."
)
mat["r16_measurement_limit"] = (
    "The Purdue entrance images are uncalibrated perspective photos; shader values, "
    "brick dimensions, mortar dimensions, bond and facade assignments remain estimates."
)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
print("R16_SAVE", OUT)
print("brick_color_1", tuple(brick.inputs["Color1"].default_value))
print("brick_color_2", tuple(brick.inputs["Color2"].default_value))
print("mortar", tuple(brick.inputs["Mortar"].default_value), brick.inputs["Mortar Size"].default_value)
