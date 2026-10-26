"""Refresh the passing Wiley R2 building library in the campus master."""
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
REPORT_PATH = ROOT / "audit/master_sync_r25.json"
ASSET_ID = "wiley_hall"
ASSET_PATH = MODULAR / "buildings/wiley_hall.blend"
EXPECTED_SHA256 = "8f3e904273ec680811163d8150098aa0f67f55705376df86359b8510cc3a3859"
EXPECTED_OBJECTS = 398
SHELL_OBJECT = "Wiley | lightly weathered buff limestone.005"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if Path(bpy.data.filepath).resolve() != MASTER.resolve():
    raise RuntimeError("Start Blender with purdue_campus_master.blend already loaded")
manifest = read_json(MANIFEST_PATH)
verification = read_json(VERIFICATION_PATH)
grade = read_json(ROOT / "audit/wiley_hall/independent_grade_r2.json")
reopen = read_json(ROOT / "audit/wiley_hall/independent_reopen_r2.json")
marker_evidence = read_json(ROOT / "audit/wiley_hall/independent_grade_r2_marker.json")
mesh_bounds = read_json(ROOT / "audit/wiley_hall/mesh_bounds_r2.json")
asset_path = ASSET_PATH.resolve()
asset_hash = hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()
if verification.get("status") != "PASS":
    raise RuntimeError("Existing modular verification is not PASS")
if asset_hash != EXPECTED_SHA256 or grade.get("sha256") != asset_hash:
    raise RuntimeError("Wiley R2 asset hash does not match its independent grade")
if not grade.get("passed") or float(grade.get("score", 0)) < 8.0:
    raise RuntimeError("Wiley R2 has no passing independent grade")
if reopen.get("sha256") != asset_hash or not reopen.get("reopened_saved_asset"):
    raise RuntimeError("Wiley independent reopen does not match the saved asset")
if int(reopen.get("export_collection_object_count", -1)) != EXPECTED_OBJECTS:
    raise RuntimeError("Wiley R2 export count does not match fresh reopen")
if reopen.get("materialless_meshes") or reopen.get("missing_external_images"):
    raise RuntimeError("Wiley R2 has material or image portability issues")
if marker_evidence.get("read_only_reopen") is not True or marker_evidence.get("marker") != "Placement_wiley_hall":
    raise RuntimeError("Independent master-placement audit does not identify the Wiley marker")

record = next((item for item in manifest["assets"] if item["id"] == ASSET_ID), None)
if record is None or record.get("kind") != "detailed":
    raise RuntimeError("Manifest does not describe Wiley Hall as a detailed asset")
collection_name = record["collection"]
collection = bpy.data.collections.get(collection_name)
marker = bpy.data.objects.get("Placement_wiley_hall")
if collection is None or collection.library is None or marker is None:
    raise RuntimeError("Master is missing Wiley's linked collection or placement marker")
if Path(bpy.path.abspath(collection.library.filepath)).resolve() != asset_path:
    raise RuntimeError("Wiley master link points to an unexpected source file")
collection.library.reload()
collection = bpy.data.collections.get(collection_name)
marker = bpy.data.objects.get("Placement_wiley_hall")
if collection is None or marker is None or marker.instance_collection != collection:
    raise RuntimeError("Wiley library reload lost its collection instance")
objects = list(collection.all_objects)
if len(objects) != EXPECTED_OBJECTS:
    raise RuntimeError(f"Wiley master link has {len(objects)} objects, expected {EXPECTED_OBJECTS}")
origin = record.get("placement_origin_xy_m")
if not origin or len(origin) != 2:
    raise RuntimeError("Wiley manifest placement origin is missing")
position_error = ((float(marker.location.x) - float(origin[0])) ** 2 +
                  (float(marker.location.y) - float(origin[1])) ** 2) ** 0.5
if position_error > 0.001 or abs(float(marker.location.z)) > 0.001:
    raise RuntimeError(f"Wiley marker differs from its manifest origin by {position_error:.6f} m")
if any(abs(float(value) - 1.0) > 1e-6 for value in marker.scale):
    raise RuntimeError("Wiley master marker scale changed")
if any(abs(float(value)) > 1e-6 for value in marker.rotation_euler):
    raise RuntimeError("Wiley master marker rotation changed")
if any(child.name == collection_name for child in bpy.context.scene.collection.children):
    raise RuntimeError("Wiley source collection is directly linked to scene root and may be duplicated")

local_bounds = reopen["evaluated_mesh_bounds_local_axis_major_m"]
shell_local_bounds = mesh_bounds.get(SHELL_OBJECT)
if shell_local_bounds is None:
    raise RuntimeError(f"Independent bounds evidence lacks structural shell proxy {SHELL_OBJECT}")
shell_world_bounds = [
    [float(shell_local_bounds[0][i]) + float(origin[i]), float(shell_local_bounds[1][i]) + float(origin[i])]
    if i < 2 else [float(shell_local_bounds[0][i]), float(shell_local_bounds[1][i])]
    for i in range(3)
]
record["objects"] = [obj.name for obj in objects]
record["object_count"] = len(objects)
record["local_bounds_m"] = local_bounds
record["bounds_world_m"] = [
    [float(local_bounds[i][0]) + float(origin[i]), float(local_bounds[i][1]) + float(origin[i])]
    if i < 2 else [float(local_bounds[i][0]), float(local_bounds[i][1])]
    for i in range(3)
]
record["exterior_bounds_world_m"] = shell_world_bounds
record["accuracy_status"] = (
    "independently graded 8.3/10; R2 asset and existing master placement marker verified against WILY "
    "OBJECTID 290; shell bbox center agrees with the converted campus GIS ring within about 0.03 m; "
    "shell bounds remain about 10 m short per axis and need a structural wall overlay before any resizing; "
    "large lawn/road context is excluded from Asset_wiley_hall; interiors remain schematic"
)
record["independent_grade_file"] = "../audit/wiley_hall/independent_grade_r2.md"
record["evidence_file"] = "../audit/wiley_hall/independent_reopen_r2.json"
record["asset_sha256"] = asset_hash

scene = bpy.context.scene
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
        "object_count": len(objects),
        "collection": collection_name,
        "library_path": bpy.path.relpath(str(asset_path)),
        "placement_marker": marker.name,
        "marker_xy_m": [float(marker.location.x), float(marker.location.y)],
        "manifest_xy_m": [float(origin[0]), float(origin[1])],
        "placement_error_m": position_error,
        "shell_bounds_world_m": shell_world_bounds,
    }],
    "notes": ["Oversized lawn, road, and road-marking context meshes remain preserved outside the export collection."],
}
write_json(REPORT_PATH, report)
print(json.dumps(report, indent=2, ensure_ascii=False))
