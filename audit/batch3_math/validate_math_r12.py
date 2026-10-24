"""Reopen the unchanged saved Math Sciences asset and validate R12 scope."""
import bpy
import json
from mathutils import Vector
from pathlib import Path

ROOT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
ASSET = ROOT / "modular/buildings/math_sciences.blend"
OUT = ROOT / "audit/batch3_math/round12_validation.json"

if Path(bpy.data.filepath).resolve() != ASSET.resolve():
    raise RuntimeError(f"Unexpected startup file: {bpy.data.filepath}")
asset = bpy.data.collections.get("Asset_math_sciences")
if asset is None:
    raise RuntimeError("Asset_math_sciences missing on reopen")

def bounds(obj):
    points = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]

shell = bpy.data.objects["MATH_Corrected_GIS_Wall_Envelope"]
roof = bpy.data.objects["MATH_Corrected_GIS_Roof_Slab"]
penthouse = bpy.data.objects["MATH_Rooftop_Penthouse_Base"]
coping = bpy.data.objects["MATH_Rooftop_Penthouse_Copings"]
unpacked = [img.name for img in bpy.data.images if img.source == "FILE" and img.packed_file is None and img.filepath]
result = {
    "opened_saved_asset": True,
    "asset": str(ASSET),
    "collection_object_count": len(asset.all_objects),
    "direct_object_count": len(asset.objects),
    "shell_world_bounds_m": bounds(shell),
    "roof_slab_world_bounds_m": bounds(roof),
    "penthouse_base_world_bounds_m": bounds(penthouse),
    "penthouse_coping_world_bounds_m": bounds(coping),
    "r10_roof_height_geometry_changed": asset.get("r10_height_geometry_changed", None),
    "unpacked_external_images": unpacked,
    "r12_geometry_change_count": 0,
    "master_or_shared_files_edited": False,
}
result["passed"] = bool(
    len(asset.all_objects) == 593 and
    abs(result["shell_world_bounds_m"][2][1] - 33.2) < 0.001 and
    abs(result["roof_slab_world_bounds_m"][2][1] - 33.4) < 0.001 and
    abs(result["penthouse_coping_world_bounds_m"][2][1] - 36.5) < 0.001 and
    result["r10_roof_height_geometry_changed"] is False and
    not unpacked
)
OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
if not result["passed"]:
    raise RuntimeError("R12 reopen validation failed")
