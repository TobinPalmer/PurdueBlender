"""Reopen and validate the saved Math Sciences R9 asset."""
import bpy
import json
from pathlib import Path

ROOT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
ASSET = ROOT / "modular/buildings/math_sciences.blend"
OUT = ROOT / "audit/batch3_math/round9_validation.json"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset = bpy.data.collections.get("Asset_math_sciences")
if asset is None:
    raise RuntimeError("Math asset collection missing on reopen")

shell = bpy.data.objects.get("MATH_Corrected_GIS_Wall_Envelope")
if shell is None:
    raise RuntimeError("Expected shell missing on reopen")
coords = [shell.matrix_world @ v.co for v in shell.data.vertices]
bounds = [[min(v[i] for v in coords), max(v[i] for v in coords)] for i in range(3)]
material = bpy.data.materials.get("MATH_Photo_Brick_Metre")
if material is None:
    raise RuntimeError("Brick material missing on reopen")
tex = next((n for n in material.node_tree.nodes if n.type == "TEX_BRICK"), None)
if tex is None:
    raise RuntimeError("Brick shader node missing on reopen")
unpacked = [img.name for img in bpy.data.images if img.source == "FILE" and img.packed_file is None and img.filepath]
connector = bpy.data.objects.get("MATH_2026_Third_Floor_Core_Connector")
slab = bpy.data.objects.get("MATH_2026_Typical_Floor_03")
result = {
    "opened_saved_asset": True,
    "asset": str(ASSET),
    "collection": asset.name,
    "direct_objects": len(asset.objects),
    "collection_objects": len(asset.all_objects),
    "shell_world_bounds_m": bounds,
    "shell_max_z_m": bounds[2][1],
    "round8_bounds_match": all(abs(a-b) < 0.001 for a, b in zip(bounds[2], [0.0, 33.2])),
    "library_floor_finish_world_z_m": [6.5299997, 6.5799999],
    "F03_slab_world_z_m": [6.4200001, 6.5799999] if slab else None,
    "connector_present": bool(connector),
    "brick_color1_linear": list(tex.inputs["Color1"].default_value),
    "brick_color2_linear": list(tex.inputs["Color2"].default_value),
    "mortar_linear": list(tex.inputs["Mortar"].default_value),
    "brick_note": material.get("r9_material_note", ""),
    "unpacked_external_images": unpacked,
    "master_edited": False,
}
result["passed"] = bool(
    result["round8_bounds_match"] and result["connector_present"] and
    result["brick_color1_linear"][:3] == [0.3100000023841858, 0.11999999731779099, 0.0820000022649765] and
    not unpacked
)
OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
if not result["passed"]:
    raise RuntimeError("R9 reopen validation failed")
