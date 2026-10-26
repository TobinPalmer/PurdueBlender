"""Verify the saved Rawls integration after opening the master in a new process."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "purdue_campus_master.blend"
ASSET = ROOT / "modular/buildings/rawls_hall.blend"
MANIFEST = ROOT / "modular/manifest.json"
REPORT = ROOT / "audit/master_sync_r23.json"
EXPECTED_SHA256 = "19d2ec5828daee8b2529d8b0790422b9a43a9f795b41c6fb2e6bc8c21e1ec9eb"
EXPECTED_OBJECTS = 761


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


if Path(bpy.data.filepath).resolve() != MASTER.resolve():
    raise RuntimeError("Verifier must run with the saved campus master opened as the startup file")
asset_hash = hashlib.sha256(ASSET.read_bytes()).hexdigest()
if asset_hash != EXPECTED_SHA256:
    raise RuntimeError(f"Rawls asset changed after grading: {asset_hash}")
manifest = read_json(MANIFEST)
record = next(item for item in manifest["assets"] if item["id"] == "rawls_hall")
collection_name = record["collection"]
collection = bpy.data.collections.get(collection_name)
marker = bpy.data.objects.get("Placement_rawls_hall")
scene = bpy.context.scene
if collection is None or collection.library is None or marker is None:
    raise RuntimeError("Freshly reopened master is missing Rawls Hall library or placement marker")
if marker.instance_collection != collection:
    raise RuntimeError("Freshly reopened Rawls placement marker does not instance the linked collection")
library_path = Path(bpy.path.abspath(collection.library.filepath)).resolve()
if library_path != ASSET.resolve():
    raise RuntimeError(f"Freshly reopened master points to the wrong asset: {library_path}")
if len(collection.all_objects) != EXPECTED_OBJECTS:
    raise RuntimeError(f"Linked collection has {len(collection.all_objects)} objects, expected {EXPECTED_OBJECTS}")
if any(child.name == collection_name for child in scene.collection.children):
    raise RuntimeError("Rawls collection is directly linked to the scene root and may be duplicated")
origin = record["placement_origin_xy_m"]
placement_error = ((float(marker.location.x) - float(origin[0])) ** 2 +
                   (float(marker.location.y) - float(origin[1])) ** 2) ** 0.5
if placement_error > 0.001 or abs(float(marker.location.z)) > 0.001:
    raise RuntimeError(f"Placement error is {placement_error:.6f} m")
if int(record.get("object_count", -1)) != EXPECTED_OBJECTS or record.get("asset_sha256") != asset_hash:
    raise RuntimeError("Manifest does not describe the independently graded Rawls asset")
report = read_json(REPORT)
report["status"] = "PASS"
report["master_reopened_after_save"] = True
report["scene_object_count"] = len(scene.objects)
report["placement_marker_count"] = sum(1 for obj in scene.objects if obj.name.startswith("Placement_"))
report["refreshed"][0]["placement_error_m"] = placement_error
REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
