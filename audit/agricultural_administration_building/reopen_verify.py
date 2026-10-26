"""Reopen and verify the Agricultural Administration Building source library."""
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSET_ID = "agricultural_administration_building"
COLLECTION = "Asset_agricultural_administration_building"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
MANIFEST_PATH = ROOT / "modular" / "manifest.json"
manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
record = next(x for x in manifest["assets"] if x.get("id") == ASSET_ID)
assert record["file"].replace("\\", "/") == f"buildings/{ASSET_ID}.blend"
assert record["collection"] == COLLECTION
coll = bpy.data.collections.get(COLLECTION)
assert coll is not None, f"Missing exported collection: {COLLECTION}"
objects = list(coll.all_objects)
assert objects, "Export collection is empty"
shell = bpy.data.objects.get("AGAD_GIS_outline_primary_shell")
assert shell is not None and shell.name in {o.name for o in objects}

depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated = shell.evaluated_get(depsgraph)
mesh = evaluated.to_mesh()
coords = [evaluated.matrix_world @ v.co for v in mesh.vertices]
evaluated.to_mesh_clear()
bounds = [min(v.x for v in coords), max(v.x for v in coords),
          min(v.y for v in coords), max(v.y for v in coords),
          min(v.z for v in coords), max(v.z for v in coords)]
expected_xy = [-34.16370847223253, 29.25791891784825,
               -25.56738044363243, 16.567859589323177]
xy_error = max(abs(a - b) for a, b in zip(bounds[:4], expected_xy))
assert xy_error < 0.02, f"GIS shell horizontal bounds mismatch: {bounds}"
assert abs(bounds[4]) < 1e-5 and abs(bounds[5] - 17.2) < 0.02, bounds

non_identity = []
for obj in objects:
    # Asset components are in local geometry coordinates. Placement is owned by
    # the master collection-instance marker, not object transforms in this file.
    if any(abs(v) > 1e-5 for v in obj.location) or any(abs(v - 1.0) > 1e-5 for v in obj.scale):
        non_identity.append(obj.name)
assert not non_identity, f"Non-local transforms found in exported objects: {non_identity}"

external_images = [img.filepath for img in bpy.data.images if img.source == "FILE"]
expected_names = set(record.get("objects", []))
actual_names = {obj.name for obj in objects}
component_names = set()
for obj in objects:
    if "component_names" in obj:
        component_names.update(json.loads(obj["component_names"]))
required_entrance_components = {
    "entrance_limestone_left_jamb",
    "entrance_limestone_right_jamb",
    "entrance_limestone_lintel",
    "entrance_glazing_full_height",
    "entrance_glazing_vertical_mullion",
    "entrance_door_pair_lower_rail",
}
missing_entrance_components = sorted(required_entrance_components - component_names)
assert not missing_entrance_components, missing_entrance_components
result = {
    "verified_at_utc": datetime.now(timezone.utc).isoformat(),
    "opened_asset": str(ASSET),
    "asset_exists": ASSET.is_file(),
    "manifest_id_asset_and_collection_match": True,
    "export_collection": COLLECTION,
    "exported_object_count": len(objects),
    "exported_object_names": sorted(actual_names),
    "manifest_object_name_count": len(expected_names),
    "manifest_object_names_missing_from_rebuilt_asset": sorted(expected_names - actual_names),
    "unexpected_export_object_names_vs_manifest": sorted(actual_names - expected_names),
    "manifest_object_names_exactly_match": expected_names == actual_names,
    "shell_name": shell.name,
    "evaluated_shell_bounds_local_m": [round(v, 5) for v in bounds],
    "expected_xy_bounds_local_m": expected_xy,
    "maximum_xy_bound_error_m": round(xy_error, 6),
    "exported_objects_have_local_identity_transforms": True,
    "external_file_image_dependencies": external_images,
    "preview_collection_present": bpy.data.collections.get("AGAD_Preview_Only") is not None,
    "preview_objects_in_export_collection": sorted(o.name for o in objects if o.name.startswith("AGAD_Preview")),
    "photo_matched_tall_entrance_components_present": sorted(required_entrance_components),
    "tall_entrance_component_names_found": sorted(required_entrance_components & component_names),
    "notes": [
        "The manifest asset ID, path, and exported collection name match exactly.",
        "Vertical height and spacing remain diagrammatic because the current GIS vertical fields have no documented units or semantics."
    ]
}
assert result["asset_exists"]
assert not external_images, f"Unexpected external image dependencies: {external_images}"
assert expected_names == actual_names, f"Manifest object list differs: {expected_names ^ actual_names}"
(HERE / "reopen_verification.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2), flush=True)
