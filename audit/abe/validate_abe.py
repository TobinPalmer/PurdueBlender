"""Reopen and validate the standalone ABE modular asset."""
import bpy
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "validation.json"
ASSET_ID = "agricultural_and_biological_engineering_abe"
COLLECTION = "Asset_" + ASSET_ID
PLACEMENT_ORIGIN = (-246.71846085020562, -632.8773862787382)
EXPECTED_CAMPUS_BOUNDS = {"x": [-282.721, -213.684], "y": [-660.474, -605.673]}

root = bpy.data.collections.get(COLLECTION)
assert root is not None, f"Missing exported collection {COLLECTION}"
objects = list(root.all_objects)
assert objects, "Export collection is empty"
shell = next((obj for obj in objects if obj.get("source_geometry") == "Purdue GIS feature 406 outer ring"), None)
assert shell is not None and shell.type == "MESH", f"Missing primary GIS shell; expected {SHELL}"
assert shell.name in {obj.name for obj in objects}, "Primary shell is outside exported collection"
assert root.get("building_id") == ASSET_ID, "Building ID metadata mismatch"
assert root.get("source_feature_id") == 406, "Source feature metadata missing"
assert root.get("coordinate_frame", "").startswith("Building-local XY"), "Asset coordinate frame metadata missing"
assert all(abs(a - b) < 1e-8 for a, b in zip(root.get("placement_origin_xy_m", []), PLACEMENT_ORIGIN)), (
    "Manifest placement origin mismatch"
)

deps = []
for image in bpy.data.images:
    if image.source == "FILE" and image.filepath and not image.packed_file:
        deps.append(image.filepath)
assert not deps, f"External image dependencies: {deps}"

corners = [shell.matrix_world @ __import__("mathutils").Vector(corner) for corner in shell.bound_box]
bounds = {
    axis: [round(min(getattr(v, axis) for v in corners), 3), round(max(getattr(v, axis) for v in corners), 3)]
    for axis in ("x", "y", "z")
}
assert 16.0 <= bounds["z"][1] <= 20.0, f"Unexpected shell height bounds: {bounds['z']}"
assert max(abs(v) for axis in ("x", "y") for v in bounds[axis]) < 50.0, f"Geometry is not building-local: {bounds}"
assert bounds["x"][1] - bounds["x"][0] > 50.0
assert bounds["y"][1] - bounds["y"][0] > 40.0
campus_bounds = {
    "x": [round(v + PLACEMENT_ORIGIN[0], 3) for v in bounds["x"]],
    "y": [round(v + PLACEMENT_ORIGIN[1], 3) for v in bounds["y"]],
}
for axis in ("x", "y"):
    assert all(abs(a - b) < 0.02 for a, b in zip(campus_bounds[axis], EXPECTED_CAMPUS_BOUNDS[axis])), (
        f"Manifest translation does not recover the GIS footprint on {axis}: {campus_bounds[axis]}"
    )
assert len(objects) > 500, f"Expected detailed facade geometry, found {len(objects)} objects"

result = {
    "reopened_asset": str(bpy.data.filepath),
    "reopened_asset_successfully": True,
    "building_id": root.get("building_id"),
    "collection": COLLECTION,
    "object_count": len(objects),
    "primary_shell": shell.name,
    "primary_shell_bounds_m": bounds,
    "placement_origin_xy_m": list(PLACEMENT_ORIGIN),
    "bounds_after_manifest_translation_m": campus_bounds,
    "manifest_translation_recovers_gis_footprint": True,
    "external_unpacked_image_dependencies": deps,
    "missing_collection": False,
    "missing_shell": False,
    "validation": "passed",
}
OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result))
