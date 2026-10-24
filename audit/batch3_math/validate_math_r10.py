"""Reopen and validate Math Sciences R10 evidence-only annotations."""
import bpy
import json
from mathutils import Vector
from pathlib import Path

ROOT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
ASSET = ROOT / "modular/buildings/math_sciences.blend"
OUT = ROOT / "audit/batch3_math/round10_validation.json"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset = bpy.data.collections.get("Asset_math_sciences")
if asset is None:
    raise RuntimeError("Asset_math_sciences missing on reopen")

def world_bounds(obj):
    pts = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    return [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)]

shell = bpy.data.objects["MATH_Corrected_GIS_Wall_Envelope"]
roof = bpy.data.objects["MATH_Corrected_GIS_Roof_Slab"]
penthouse = bpy.data.objects["MATH_Rooftop_Penthouse_Base"]
coping = bpy.data.objects["MATH_Rooftop_Penthouse_Copings"]
annotation_names = [roof.name, penthouse.name, coping.name]
annotation_checks = {
    name: bool(bpy.data.objects[name].get("r10_surface_source") and
               bpy.data.objects[name].get("r10_surface_height_evidence") and
               bpy.data.objects[name].get("r10_model_vs_raster_note"))
    for name in annotation_names
}
unpacked = [img.name for img in bpy.data.images if img.source == "FILE" and img.packed_file is None and img.filepath]
result = {
    "opened_saved_asset": True,
    "asset": str(ASSET),
    "collection_object_count": len(asset.all_objects),
    "direct_object_count": len(asset.objects),
    "shell_world_bounds_m": world_bounds(shell),
    "roof_slab_world_bounds_m": world_bounds(roof),
    "penthouse_base_world_bounds_m": world_bounds(penthouse),
    "penthouse_coping_world_bounds_m": world_bounds(coping),
    "roof_objects_have_r10_provenance": annotation_checks,
    "height_evidence_method": asset.get("r10_height_evidence_method", ""),
    "height_geometry_changed_flag": asset.get("r10_height_geometry_changed", None),
    "east_sign_absent": bpy.data.objects.get("MATH_Signage_East") is None,
    "unpacked_external_images": unpacked,
    "master_or_shared_files_edited": False,
}
result["passed"] = bool(
    len(asset.all_objects) == 593 and
    abs(result["shell_world_bounds_m"][2][1] - 33.2) < 0.001 and
    all(annotation_checks.values()) and
    result["height_geometry_changed_flag"] is False and
    result["east_sign_absent"] and not unpacked
)
OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
if not result["passed"]:
    raise RuntimeError("R10 asset reopen validation failed")
