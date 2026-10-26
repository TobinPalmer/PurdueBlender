"""Fresh-process validation of the R26 master libraries and placement markers."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "purdue_campus_master.blend"
MANIFEST_PATH = ROOT / "modular/manifest.json"
REPORT_PATH = ROOT / "audit/master_sync_r26.json"
EXPECTED = {
    "rawls_hall": ("modular/buildings/rawls_hall.blend", "19d2ec5828daee8b2529d8b0790422b9a43a9f795b41c6fb2e6bc8c21e1ec9eb", 761),
    "walc": ("modular/buildings/walc.blend", "71dd7f551168b9940db616c2bdde548f4df0835a8bf496037e8100e3f0f6cd5e", 969),
    "wiley_hall": ("modular/buildings/wiley_hall.blend", "8f3e904273ec680811163d8150098aa0f67f55705376df86359b8510cc3a3859", 398),
    "university_hall": ("modular/buildings/university_hall.blend", "7ed748bb216108115986f276cb5558a445559be75245be95639158221d8538c1", 1377),
    "massing_st_thomas_aquinas_5535390": (
        "modular/buildings/massing_st_thomas_aquinas_5535390.blend",
        "ec8ba6235c6a356ad81ab8b7ad8fcbe3bcc75c4071a310287ea3bb517ad5b7db",
        1204,
    ),
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


if Path(bpy.data.filepath).resolve() != MASTER.resolve():
    raise RuntimeError("Verifier must start with the saved campus master open")
manifest = read_json(MANIFEST_PATH)
scene = bpy.context.scene
verified = []
for asset_id, (relative_path, expected_hash, expected_count) in EXPECTED.items():
    record = next((item for item in manifest["assets"] if item["id"] == asset_id), None)
    if record is None or record.get("kind") != "detailed":
        raise RuntimeError(f"{asset_id} is not indexed as a detailed placement")
    asset_path = (ROOT / relative_path).resolve()
    actual_hash = hashlib.sha256(asset_path.read_bytes()).hexdigest()
    if actual_hash != expected_hash:
        raise RuntimeError(f"{asset_id} asset hash differs from the reviewed snapshot")
    collection = bpy.data.collections.get(record["collection"])
    marker_name = "Placement_" + asset_id
    marker = bpy.data.objects.get(marker_name)
    if collection is None or collection.library is None or marker is None:
        raise RuntimeError(f"{asset_id} collection or placement marker is missing")
    if marker.instance_collection != collection:
        raise RuntimeError(f"{asset_id} marker instances the wrong linked collection")
    library_path = Path(bpy.path.abspath(collection.library.filepath)).resolve()
    if library_path != asset_path:
        raise RuntimeError(f"{asset_id} points to the wrong source library")
    if len(collection.all_objects) != expected_count or record.get("object_count") != expected_count:
        raise RuntimeError(f"{asset_id} collection/manifest object count differs from expected")
    if any(child.name == record["collection"] for child in scene.collection.children):
        raise RuntimeError(f"{asset_id} source collection is directly linked in addition to its marker")
    origin = record.get("placement_origin_xy_m")
    if not origin or len(origin) != 2:
        raise RuntimeError(f"{asset_id} has no local-asset placement origin")
    error = ((float(marker.location.x) - float(origin[0])) ** 2 +
             (float(marker.location.y) - float(origin[1])) ** 2) ** 0.5
    if error > 0.001 or abs(float(marker.location.z)) > 0.001:
        raise RuntimeError(f"{asset_id} placement marker error is {error:.6f} m")
    if any(abs(float(value) - 1.0) > 1e-6 for value in marker.scale) or any(abs(float(value)) > 1e-6 for value in marker.rotation_euler):
        raise RuntimeError(f"{asset_id} marker scale/rotation is not identity")
    verified.append({
        "id": asset_id,
        "sha256": actual_hash,
        "object_count": expected_count,
        "collection": record["collection"],
        "library_path": bpy.path.relpath(str(asset_path)),
        "placement_marker": marker_name,
        "marker_xy_m": [float(marker.location.x), float(marker.location.y)],
        "manifest_xy_m": [float(origin[0]), float(origin[1])],
        "placement_error_m": error,
    })
placement_count = sum(1 for obj in scene.objects if obj.name.startswith("Placement_"))
if placement_count != 70:
    raise RuntimeError(f"Expected 70 placement markers, found {placement_count}")
report = read_json(REPORT_PATH)
report["status"] = "PASS"
report["master_reopened_after_save"] = True
report["scene_name"] = scene.name
report["scene_object_count"] = len(scene.objects)
report["placement_marker_count"] = placement_count
report["manifest_source_object_count"] = sum(int(item.get("object_count", 0)) for item in manifest["assets"])
report["refreshed"] = verified
report["candidate_assets_pending_grade"] = [
    {"id": "massing_st_thomas_aquinas_5535390", "grade": 7.7, "status": "below_threshold_R4_needed"}
]
REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
