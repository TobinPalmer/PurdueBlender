"""Coordinator-only integration of independently graded Rawls Hall R11."""
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
REPORT_PATH = ROOT / "audit/master_sync_r23.json"
ASSET_ID = "rawls_hall"
ASSET_PATH = MODULAR / "buildings/rawls_hall.blend"
EXPECTED_SHA256 = "19d2ec5828daee8b2529d8b0790422b9a43a9f795b41c6fb2e6bc8c21e1ec9eb"
EXPECTED_OBJECTS = 761
GRADE_PATH = "../audit/batch4_rawls/independent_review_round11.md"
EVIDENCE_PATH = "audit/batch4_rawls/independent_reopen_r11.json"

if Path(bpy.data.filepath).resolve() != MASTER.resolve():
    raise RuntimeError("Start Blender with purdue_campus_master.blend already loaded; open_mainfile resets this script")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


manifest = read_json(MANIFEST_PATH)
verification = read_json(VERIFICATION_PATH)
grade_path = ROOT / "audit/batch4_rawls/independent_grade_r11.json"
reopen_path = ROOT / "audit/batch4_rawls/independent_reopen_r11.json"
exterior_bounds_path = ROOT / "audit/batch4_rawls/asset_bounds_r11.json"
grade = read_json(grade_path)
reopen = read_json(reopen_path)
exterior_bounds = read_json(exterior_bounds_path)
asset_path = ASSET_PATH.resolve()
asset_hash = hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()

if verification.get("status") != "PASS":
    raise RuntimeError("Existing modular verification is not PASS")
if asset_hash != EXPECTED_SHA256:
    raise RuntimeError(f"Rawls Hall asset hash mismatch: {asset_hash}")
if not grade.get("passed") or float(grade.get("score", 0)) < 8.0 or float(grade.get("max_score", 0)) != 10.0:
    raise RuntimeError("Rawls Hall R11 does not have a passing independent grade")
if not reopen.get("reopened_saved_asset") or reopen.get("sha256") != asset_hash:
    raise RuntimeError("Rawls Hall R11 independent reopen does not match the saved asset")
if int(reopen.get("export_collection_object_count", -1)) != EXPECTED_OBJECTS:
    raise RuntimeError("Rawls Hall R11 reopen object count is unexpected")
if reopen.get("materialless_meshes") or reopen.get("missing_external_images"):
    raise RuntimeError("Rawls Hall R11 has missing materials or external images")
if exterior_bounds.get("sha256") != asset_hash or exterior_bounds.get("mesh_count") != 753:
    raise RuntimeError("Rawls Hall asset-bound evidence does not match the passing R11 asset")

record = next((item for item in manifest["assets"] if item["id"] == ASSET_ID), None)
if record is None:
    raise RuntimeError(f"Manifest is missing {ASSET_ID}")
collection_name = record["collection"]
scene = bpy.context.scene
collection = bpy.data.collections.get(collection_name)
marker = bpy.data.objects.get(f"Placement_{ASSET_ID}")
if collection is None or collection.library is None or marker is None:
    raise RuntimeError("Master is missing Rawls Hall's linked collection or placement marker")
if Path(bpy.path.abspath(collection.library.filepath)).resolve() != asset_path:
    raise RuntimeError("Rawls Hall linked collection points to an unexpected source file")
if any(child.name == collection_name for child in scene.collection.children):
    raise RuntimeError("Rawls Hall source collection is directly linked to the scene root")

# Explicitly refresh only the passing Rawls Hall library.
collection.library.reload()
collection = bpy.data.collections.get(collection_name)
marker = bpy.data.objects.get(f"Placement_{ASSET_ID}")
if collection is None or marker is None or marker.instance_collection != collection:
    raise RuntimeError("Rawls Hall library reload lost its master placement instance")
objects = list(collection.all_objects)
if len(objects) != EXPECTED_OBJECTS:
    raise RuntimeError(f"Rawls Hall master link has {len(objects)} objects, expected {EXPECTED_OBJECTS}")

origin = record.get("placement_origin_xy_m")
if not origin or len(origin) != 2:
    raise RuntimeError("Rawls Hall manifest placement origin is missing or malformed")
position_error = ((float(marker.location.x) - float(origin[0])) ** 2 +
                  (float(marker.location.y) - float(origin[1])) ** 2) ** 0.5
if position_error > 0.001 or abs(float(marker.location.z)) > 0.001:
    raise RuntimeError(f"Rawls Hall marker differs from its manifest origin by {position_error:.6f} m")
if any(abs(float(value) - 1.0) > 1e-6 for value in marker.scale):
    raise RuntimeError("Rawls Hall master marker scale changed")
if any(abs(float(value)) > 1e-6 for value in marker.rotation_euler):
    raise RuntimeError("Rawls Hall master marker rotation changed")

local_bounds = exterior_bounds["bounds_local_axis_major_m"]
record["objects"] = [obj.name for obj in objects]
record["object_count"] = len(objects)
record["local_bounds_m"] = local_bounds
record["bounds_world_m"] = [
    [float(local_bounds[i][0]) + float(origin[i]), float(local_bounds[i][1]) + float(origin[i])]
    if i < 2 else [float(local_bounds[i][0]), float(local_bounds[i][1])]
    for i in range(3)
]
record["accuracy_status"] = (
    "independently graded 8.14/10; R11 asset and master placement marker verified; the 44-pane "
    "southeast facade and Room 1086 sightline remain schematic with approximately 1 m plan-to-shell "
    "registration uncertainty; upper-floor circulation is unverified"
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

report = {
    "status": "SAVED_PENDING_FRESH_REOPEN",
    "master": str(MASTER),
    "master_reopened_after_save": False,
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
        "placement_error_m": position_error,
    }],
    "notes": ["Only the passing Rawls Hall library was explicitly reloaded; only overall asset bounds were refreshed. Run verify_rawls_r23.py in a fresh Blender process before treating integration as passed."],
}
write_json(REPORT_PATH, report)
print(json.dumps(report, indent=2, ensure_ascii=False))






