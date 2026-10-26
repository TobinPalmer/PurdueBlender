"""Verify the WALC R5 library in a fresh process after saving the master."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "purdue_campus_master.blend"
ASSET = ROOT / "modular/buildings/walc.blend"
MANIFEST = ROOT / "modular/manifest.json"
REPORT = ROOT / "audit/master_sync_r24.json"
EXPECTED_SHA256 = "71dd7f551168b9940db616c2bdde548f4df0835a8bf496037e8100e3f0f6cd5e"
EXPECTED_OBJECTS = 969


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


if Path(bpy.data.filepath).resolve() != MASTER.resolve():
    raise RuntimeError("Verifier must start with the saved master file already open")
asset_hash = hashlib.sha256(ASSET.read_bytes()).hexdigest()
if asset_hash != EXPECTED_SHA256:
    raise RuntimeError(f"WALC asset changed after grading: {asset_hash}")
manifest = read_json(MANIFEST)
record = next(item for item in manifest["assets"] if item["id"] == "walc")
collection = bpy.data.collections.get(record["collection"])
marker = bpy.data.objects.get("Placement_walc")
scene = bpy.context.scene
if collection is None or collection.library is None or marker is None:
    raise RuntimeError("Fresh master is missing WALC library or placement marker")
if marker.instance_collection != collection:
    raise RuntimeError("WALC placement marker does not instance its linked collection")
library_path = Path(bpy.path.abspath(collection.library.filepath)).resolve()
if library_path != ASSET.resolve():
    raise RuntimeError(f"WALC link points to the wrong asset: {library_path}")
if len(collection.all_objects) != EXPECTED_OBJECTS:
    raise RuntimeError(f"WALC link has {len(collection.all_objects)} objects, expected {EXPECTED_OBJECTS}")
if any(child.name == collection.name for child in scene.collection.children):
    raise RuntimeError("WALC collection is linked directly to the scene root and may be duplicated")
origin = record["placement_origin_xy_m"]
error = ((float(marker.location.x) - float(origin[0])) ** 2 +
         (float(marker.location.y) - float(origin[1])) ** 2) ** 0.5
if error > 0.001 or abs(float(marker.location.z)) > 0.001:
    raise RuntimeError(f"WALC placement error is {error:.6f} m")
if record.get("asset_sha256") != asset_hash or record.get("object_count") != EXPECTED_OBJECTS:
    raise RuntimeError("WALC manifest metadata does not match the reviewed asset")
if sum(1 for obj in scene.objects if obj.name.startswith("Placement_")) != 69:
    raise RuntimeError("Master placement marker count changed unexpectedly")
report = read_json(REPORT)
report["status"] = "PASS"
report["master_reopened_after_save"] = True
report["scene_object_count"] = len(scene.objects)
report["placement_marker_count"] = sum(1 for obj in scene.objects if obj.name.startswith("Placement_"))
report["refreshed"][0]["placement_error_m"] = error
REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
