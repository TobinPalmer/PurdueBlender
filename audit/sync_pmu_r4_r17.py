"""Coordinator-only integration of independently graded PMU R4 into the master."""
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
REPORT_PATH = ROOT / "audit/master_sync_r17.json"
ASSET_ID = "purdue_memorial_union"
ASSET_PATH = MODULAR / "buildings/purdue_memorial_union.blend"
EXPECTED_SHA256 = "7e0e03969cad5846edacc38a4945f2c9021e48877c022cc79035d10e144eb480"
EXPECTED_OBJECTS = 650
GRADE_PATH = "../audit/purdue_memorial_union_independent_grade/independent_grade_r4.md"
EVIDENCE_PATH = "audit/purdue_memorial_union_refine/validation_r4.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


manifest = read_json(MANIFEST_PATH)
verification = read_json(VERIFICATION_PATH)
grade_path = ROOT / "audit/purdue_memorial_union_independent_grade/independent_grade_r4.json"
validation_path = ROOT / "audit/purdue_memorial_union_independent_grade/independent_reopen_r4.json"
grade = read_json(grade_path)
validation = read_json(validation_path)
asset_hash = hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()

if verification.get("status") != "PASS":
    raise RuntimeError("Existing modular verification is not PASS")
if asset_hash != EXPECTED_SHA256:
    raise RuntimeError(f"PMU asset hash mismatch: {asset_hash}")
if not grade.get("passed") or float(grade.get("score", 0)) < 8.0 or float(grade.get("max_score", 0)) != 10.0:
    raise RuntimeError("PMU R4 does not have a passing independent grade")
if validation.get("sha256") != asset_hash or not validation.get("reopened_saved_asset"):
    raise RuntimeError("PMU R4 independent reopen does not match the saved asset")
if int(validation.get("collection_objects", -1)) != EXPECTED_OBJECTS:
    raise RuntimeError("PMU R4 reopen object count is unexpected")

record = next((item for item in manifest["assets"] if item["id"] == ASSET_ID), None)
if record is None:
    raise RuntimeError(f"Manifest is missing {ASSET_ID}")
asset_path = ASSET_PATH.resolve()
collection_name = record["collection"]

# Only refresh the independently passing PMU library. Other unfinished building
# libraries are left for their own review and coordinator integration.
bpy.ops.wm.open_mainfile(filepath=str(MASTER))
scene = bpy.context.scene
collection = bpy.data.collections.get(collection_name)
marker = bpy.data.objects.get(f"Placement_{ASSET_ID}")
if collection is None or collection.library is None or marker is None:
    raise RuntimeError("Master is missing PMU's linked collection or placement marker")
if Path(bpy.path.abspath(collection.library.filepath)).resolve() != asset_path:
    raise RuntimeError("PMU linked collection points to an unexpected source file")
if any(child.name == collection_name for child in scene.collection.children):
    raise RuntimeError("PMU source collection is directly linked to the scene root")

collection.library.reload()
collection = bpy.data.collections.get(collection_name)
marker = bpy.data.objects.get(f"Placement_{ASSET_ID}")
if collection is None or marker is None or marker.instance_collection != collection:
    raise RuntimeError("PMU library reload lost its master placement instance")
objects = list(collection.all_objects)
if len(objects) != EXPECTED_OBJECTS:
    raise RuntimeError(f"PMU master link has {len(objects)} objects, expected {EXPECTED_OBJECTS}")

origin = record.get("placement_origin_xy_m")
if not origin or len(origin) != 2:
    raise RuntimeError("PMU manifest placement origin is missing or malformed")
position_error = ((float(marker.location.x) - float(origin[0])) ** 2 +
                  (float(marker.location.y) - float(origin[1])) ** 2) ** 0.5
if position_error > 0.001 or abs(float(marker.location.z)) > 0.001:
    raise RuntimeError(f"PMU marker is displaced from its manifest origin by {position_error:.6f} m")
if any(abs(float(value) - 1.0) > 1e-6 for value in marker.scale):
    raise RuntimeError("PMU master marker scale changed")
if any(abs(float(value)) > 1e-6 for value in marker.rotation_euler):
    raise RuntimeError("PMU master marker rotation changed")

local_bounds = validation["evaluated_collection_bounds_local_m"]
record["objects"] = [obj.name for obj in objects]
record["object_count"] = len(objects)
record["local_bounds_m"] = local_bounds
record["bounds_world_m"] = [
    [float(local_bounds[i][0]) + float(origin[i]), float(local_bounds[i][1]) + float(origin[i])]
    if i < 2 else [float(local_bounds[i][0]), float(local_bounds[i][1])]
    for i in range(3)
]
record["accuracy_status"] = (
    "independently graded 8.0/10; R4 asset and master placement verified; historic GIS supports "
    "approximate shell only; 29.5 m height, floor spacing, roof elevations and junctions remain "
    "estimated; tower reliefs and some facade details remain schematic"
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

# Verify the saved master from disk, including exact library source and placement.
bpy.ops.wm.open_mainfile(filepath=str(MASTER))
scene = bpy.context.scene
collection = bpy.data.collections.get(collection_name)
marker = bpy.data.objects.get(f"Placement_{ASSET_ID}")
if collection is None or collection.library is None or marker is None:
    raise RuntimeError("PMU disappeared on fresh master reopen")
if len(collection.all_objects) != EXPECTED_OBJECTS or marker.instance_collection != collection:
    raise RuntimeError("Fresh master reopen has an incorrect PMU collection or marker")
if Path(bpy.path.abspath(collection.library.filepath)).resolve() != asset_path:
    raise RuntimeError("Fresh master reopen points PMU to an unexpected source library")
if any(child.name == collection_name for child in scene.collection.children):
    raise RuntimeError("Fresh master reopen would directly duplicate PMU")
if ((float(marker.location.x) - float(origin[0])) ** 2 +
        (float(marker.location.y) - float(origin[1])) ** 2) ** 0.5 > 0.001:
    raise RuntimeError("Fresh master reopen changed PMU marker placement")

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
        "placement_error_m": position_error,
    }],
    "notes": ["Only the passing PMU library was explicitly reloaded by this integration."],
}
write_json(REPORT_PATH, report)
print(json.dumps(report, indent=2, ensure_ascii=False))
