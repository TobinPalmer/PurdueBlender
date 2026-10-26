"""Coordinator-only integration of independently graded Ray W. Herrick Laboratories R2."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "purdue_campus_master.blend"
MODULAR = ROOT / "modular"
MANIFEST_PATH = MODULAR / "manifest.json"
VERIFICATION_PATH = MODULAR / "verification.json"
REPORT_PATH = ROOT / "audit/master_sync_r21.json"
ASSET_ID = "ray_w_herrick_laboratories"
ASSET_PATH = MODULAR / "buildings/ray_w_herrick_laboratories.blend"
EXPECTED_SHA256 = "5dfe15ad317dad3661fab756b312e2d0ce2de9b64b53bb3ecb0523a93525bbbf"
EXPECTED_OBJECTS = 80
GRADE_PATH = "../audit/ray_w_herrick_refine/independent_grade_r2.md"
EVIDENCE_PATH = "audit/ray_w_herrick_refine/independent_reopen_r2.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


manifest = read_json(MANIFEST_PATH)
verification = read_json(VERIFICATION_PATH)
grade_path = ROOT / "audit/ray_w_herrick_refine/independent_grade_r2.json"
reopen_path = ROOT / "audit/ray_w_herrick_refine/independent_reopen_r2.json"
exterior_bounds_path = ROOT / "audit/ray_w_herrick_refine/exterior_bounds_r2.json"
grade = read_json(grade_path)
reopen = read_json(reopen_path)
exterior_bounds = read_json(exterior_bounds_path)
asset_path = ASSET_PATH.resolve()
asset_hash = hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()

if verification.get("status") != "PASS":
    raise RuntimeError("Existing modular verification is not PASS")
if asset_hash != EXPECTED_SHA256:
    raise RuntimeError(f"Ray W. Herrick Laboratories asset hash mismatch: {asset_hash}")
if not grade.get("passed") or float(grade.get("score", 0)) < 8.0 or float(grade.get("max_score", 0)) != 10.0:
    raise RuntimeError("Ray W. Herrick Laboratories R2 does not have a passing independent grade")
if not reopen.get("fresh_reopen") or reopen.get("sha256") != asset_hash:
    raise RuntimeError("Ray W. Herrick Laboratories R2 independent reopen does not match the saved asset")
if int(reopen.get("collection_object_count", -1)) != EXPECTED_OBJECTS:
    raise RuntimeError("Ray W. Herrick Laboratories R2 reopen object count is unexpected")
if reopen.get("materialless_meshes") or reopen.get("missing_external_images"):
    raise RuntimeError("Ray W. Herrick Laboratories R2 has missing materials or external images")
if exterior_bounds.get("asset_sha256") != asset_hash or exterior_bounds.get("evaluated_mesh_object_count") != 63:
    raise RuntimeError("Ray W. Herrick Laboratories exterior-bound evidence does not match the passing R2 asset")

record = next((item for item in manifest["assets"] if item["id"] == ASSET_ID), None)
if record is None:
    raise RuntimeError(f"Manifest is missing {ASSET_ID}")
collection_name = record["collection"]
bpy.ops.wm.open_mainfile(filepath=str(MASTER))
scene = bpy.context.scene
collection = bpy.data.collections.get(collection_name)
marker = bpy.data.objects.get(f"Placement_{ASSET_ID}")
if collection is None or collection.library is None or marker is None:
    raise RuntimeError("Master is missing Ray W. Herrick Laboratories's linked collection or placement marker")
if Path(bpy.path.abspath(collection.library.filepath)).resolve() != asset_path:
    raise RuntimeError("Ray W. Herrick Laboratories linked collection points to an unexpected source file")
if any(child.name == collection_name for child in scene.collection.children):
    raise RuntimeError("Ray W. Herrick Laboratories source collection is directly linked to the scene root")

# Explicitly refresh only the passing Ray W. Herrick Laboratories library.
collection.library.reload()
collection = bpy.data.collections.get(collection_name)
marker = bpy.data.objects.get(f"Placement_{ASSET_ID}")
if collection is None or marker is None or marker.instance_collection != collection:
    raise RuntimeError("Ray W. Herrick Laboratories library reload lost its master placement instance")
objects = list(collection.all_objects)
if len(objects) != EXPECTED_OBJECTS:
    raise RuntimeError(f"Ray W. Herrick Laboratories master link has {len(objects)} objects, expected {EXPECTED_OBJECTS}")

origin = record.get("placement_origin_xy_m")
if not origin or len(origin) != 2:
    raise RuntimeError("Ray W. Herrick Laboratories manifest placement origin is missing or malformed")
position_error = ((float(marker.location.x) - float(origin[0])) ** 2 +
                  (float(marker.location.y) - float(origin[1])) ** 2) ** 0.5
if position_error > 0.001 or abs(float(marker.location.z)) > 0.001:
    raise RuntimeError(f"Ray W. Herrick Laboratories marker differs from its manifest origin by {position_error:.6f} m")
if any(abs(float(value) - 1.0) > 1e-6 for value in marker.scale):
    raise RuntimeError("Ray W. Herrick Laboratories master marker scale changed")
if any(abs(float(value)) > 1e-6 for value in marker.rotation_euler):
    raise RuntimeError("Ray W. Herrick Laboratories master marker rotation changed")

local_bounds = reopen["evaluated_collection_bounds_local_m"]
record["objects"] = [obj.name for obj in objects]
record["object_count"] = len(objects)
record["local_bounds_m"] = local_bounds
record["exterior_bounds_world_m"] = exterior_bounds["world_bounds_axis_major_m"]
record["bounds_world_m"] = [
    [float(local_bounds[i][0]) + float(origin[i]), float(local_bounds[i][1]) + float(origin[i])]
    if i < 2 else [float(local_bounds[i][0]), float(local_bounds[i][1])]
    for i in range(3)
]
record["accuracy_status"] = (
    "independently graded 8.1/10; R2 HLAB asset and master placement marker verified; the "
    "foundation outline matches Purdue GIS FID 878 within the documented 0.25 m simplification "
    "tolerance but is not a surveyed wall outline; the roof, facade modules and lab interior remain schematic"
)
record["independent_grade_file"] = GRADE_PATH
record["evidence_file"] = EVIDENCE_PATH
record["asset_sha256"] = asset_hash

placement_count = sum(1 for obj in scene.objects if obj.name.startswith("Placement_"))
if placement_count != 69:
    raise RuntimeError(f"Unexpected master placement marker count: {placement_count}")
manifest["detailed_asset_count"] = sum(1 for item in manifest["assets"] if item.get("kind") == "detailed")
manifest["last_master_build"] = "2026-10-25"
verification["master_placement_markers"] = placement_count
verification["master_scene_object_count"] = len(scene.objects)
verification["source_asset_object_count"] = sum(int(item.get("object_count", 0)) for item in manifest["assets"])
if verification.get("asset_count") != len(manifest["assets"]):
    raise RuntimeError("Manifest/verification asset count mismatch")
if verification.get("building_count") != verification.get("asset_count") - 1:
    raise RuntimeError("Manifest/verification building count mismatch")
verification["status"] = "PASS"
verification["errors"] = []

bpy.ops.wm.save_as_mainfile(filepath=str(MASTER))
write_json(MANIFEST_PATH, manifest)
write_json(VERIFICATION_PATH, verification)

# Fresh disk reopen verifies linked source, object count, and placement marker.
bpy.ops.wm.open_mainfile(filepath=str(MASTER))
scene = bpy.context.scene
collection = bpy.data.collections.get(collection_name)
marker = bpy.data.objects.get(f"Placement_{ASSET_ID}")
if collection is None or collection.library is None or marker is None:
    raise RuntimeError("Ray W. Herrick Laboratories disappeared on fresh master reopen")
if len(collection.all_objects) != EXPECTED_OBJECTS or marker.instance_collection != collection:
    raise RuntimeError("Fresh master reopen has an incorrect Ray W. Herrick Laboratories collection or marker")
if Path(bpy.path.abspath(collection.library.filepath)).resolve() != asset_path:
    raise RuntimeError("Fresh master reopen points Ray W. Herrick Laboratories to an unexpected source library")
if any(child.name == collection_name for child in scene.collection.children):
    raise RuntimeError("Fresh master reopen would directly duplicate Ray W. Herrick Laboratories")
post_error = ((float(marker.location.x) - float(origin[0])) ** 2 +
              (float(marker.location.y) - float(origin[1])) ** 2) ** 0.5
if post_error > 0.001:
    raise RuntimeError(f"Fresh master reopen changed Ray W. Herrick Laboratories marker placement by {post_error:.6f} m")

report = {
    "status": "PASS",
    "master": str(MASTER),
    "master_reopened_after_save": True,
    "scene_object_count": len(scene.objects),
    "placement_marker_count": placement_count,
    "manifest_source_object_count": verification["source_asset_object_count"],
    "refreshed": [{
        "id": ASSET_ID,
        "sha256": asset_hash,
        "object_count": len(collection.all_objects),
        "collection": collection_name,
        "library_path": bpy.path.relpath(str(asset_path)),
        "placement_marker": marker.name,
        "marker_xy_m": [float(marker.location.x), float(marker.location.y)],
        "manifest_xy_m": [float(origin[0]), float(origin[1])],
        "placement_error_m": post_error,
    }],
    "notes": ["Only the passing Ray W. Herrick Laboratories library was explicitly reloaded by this integration."],
}
write_json(REPORT_PATH, report)
print(json.dumps(report, indent=2, ensure_ascii=False))





