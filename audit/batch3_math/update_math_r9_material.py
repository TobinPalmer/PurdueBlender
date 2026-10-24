"""Source-limited R9 brick material readability adjustment for Math Sciences."""
import bpy
from pathlib import Path

ROOT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
ASSET = ROOT / "modular/buildings/math_sciences.blend"

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
mat = bpy.data.materials.get("MATH_Photo_Brick_Metre")
if mat is None or not mat.use_nodes:
    raise RuntimeError("Expected embedded MATH_Photo_Brick_Metre node material")

nodes = mat.node_tree.nodes
brick = next((node for node in nodes if node.type == "TEX_BRICK"), None)
bsdf = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
if brick is None or bsdf is None:
    raise RuntimeError("Expected Brick Texture and Principled BSDF nodes")

# The Purdue Statistics image supports light red-brown brick, but it is not a
# calibrated color chart. These restrained warmer/deeper values address the
# model's pale pink campus-view appearance; they are explicitly qualitative.
brick.inputs["Color1"].default_value = (0.31, 0.12, 0.082, 1.0)
brick.inputs["Color2"].default_value = (0.43, 0.205, 0.13, 1.0)
brick.inputs["Mortar"].default_value = (0.45, 0.40, 0.35, 1.0)
mat.diffuse_color = (0.38, 0.19, 0.13, 1.0)
mat["r9_material_note"] = (
    "Qualitative red-brown adjustment from the Purdue Statistics Math Building photo; "
    "not calibrated color measurement. Roof height and unpictured north/west facade "
    "geometry remain unchanged."
)
mat["r9_evidence_url"] = "https://www.stat.purdue.edu/images/about/Math-Bldg-.jpg"
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print("R9 material updated and saved", mat.name)
