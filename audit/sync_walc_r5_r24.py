"""Refresh the independently graded WALC R5 library in the campus master."""
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
REPORT_PATH = ROOT / "audit/master_sync_r24.json"
ASSET_ID = "walc"
ASSET_PATH = MODULAR / "buildings/walc.blend"
EXPECTED_SHA256 = "71dd7f551168b9940db616c2bdde548f4df0835a8bf496037e8100e3f0f6cd5e"
EXPECTED_OBJECTS = 969


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if Path(bpy.data.filepath).resolve() != MASTER.resolve():
    raise RuntimeError("Start Blender with purdue_campus_master.blend already loaded")
manifest = read_json(MANIFEST_PATH)
verification = read_json(VERIFICATION_PATH)
grade = read_json(ROOT / "audit/walc_refine/independent_grade_r5.json")
reopen = read_json(ROOT / "audit/walc_refine/independent_grade_r5_reopen.json")
asset_path = ASSET_PATH.resolve()
asset_hash = hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()
if verification.get("status") != "PASS":
    raise RuntimeError("Existing modular verification is not PASS")
if asset_hash != EXPECTED_SHA256 or grade.get("asset_sha256") != asset_hash:
    raise RuntimeError("WALC asset hash does not match its independent grade")
if grade.get("result") != "meets_threshold" or float(grade.get("score", 0)) < 8.0:
    raise RuntimeError("WALC R5 has no passing independent grade")
if reopen.get("sha256") != asset_hash or not reopen.get("hash_matches_requested"):
    raise RuntimeError("WALC independent reopen evidence does not match the saved asset")
if int(reopen.get("collection_object_count", -1)) != EXPECTED_OBJECTS:
    raise RuntimeError("WALC R5 object count is not the independently reopened count")
if reopen.get("materialless_meshes") or reopen.get("missing_external_images"):
    raise RuntimeError("WALC R5 has missing materials or external images")
record = next((item for item in manifest["assets"] if item["id"] == ASSET_ID), None)
if record is None:
    raise RuntimeError("Manifest is missing WALC")
collection_name = record["collection"]
collection = bpy.data.collections.get(collection_name)
marker = bpy.data.objects.get("Placement_walc")
if collection is None or collection.library is None or marker is None:
    raise RuntimeError("Master is missing WALC's linked collection or placement marker")
if Path(bpy.path.abspath(collection.library.filepath)).resolve() != asset_path:
    raise RuntimeError("WALC master link points to an unexpected source file")
collection.library.reload()
collection = bpy.data.collections.get(collection_name)
marker = bpy.data.objects.get("Placement_walc")
if collection is None or marker is None or marker.instance_collection != collection:
    raise RuntimeError("WALC library reload lost its collection instance")
objects = list(collection.all_objects)
if len(objects) != EXPECTED_OBJECTS:
    raise RuntimeError(f"WALC master link has {len(objects)} objects, expected {EXPECTED_OBJECTS}")
origin = record.get("placement_origin_xy_m")
if not origin or len(origin) != 2:
    raise RuntimeError("WALC manifest placement origin is missing")
position_error = ((float(marker.location.x) - float(origin[0])) ** 2 +
                  (float(marker.location.y) - float(origin[1])) ** 2) ** 0.5
if position_error > 0.001 or abs(float(marker.location.z)) > 0.001:
    raise RuntimeError(f"WALC marker differs from its manifest origin by {position_error:.6f} m")
if any(abs(float(value) - 1.0) > 1e-6 for value in marker.scale):
    raise RuntimeError("WALC master marker scale changed")
if any(abs(float(value)) > 1e-6 for value in marker.rotation_euler):
    raise RuntimeError("WALC master marker rotation changed")

# Measure evaluated mesh vertices in the building's local coordinate frame.
depsgraph = bpy.context.evaluated_depsgraph_get()
mins = [float("inf")] * 3
maxs = [float("-inf")] * 3
mesh_count = 0
for obj in objects:
    if obj.type != "MESH":
        continue
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        world = evaluated.matrix_world
        for vertex in mesh.vertices:
            point = world @ vertex.co
            for axis in range(3):
                mins[axis] = min(mins[axis], float(point[axis]))
                maxs[axis] = max(maxs[axis], float(point[axis]))
        mesh_count += 1
    finally:
        evaluated.to_mesh_clear()
local_bounds = [[mins[i], maxs[i]] for i in range(3)]
record["objects"] = [obj.name for obj in objects]
record["object_count"] = len(objects)
record["local_bounds_m"] = local_bounds
record["bounds_world_m"] = [
    [local_bounds[i][0] + float(origin[i]), local_bounds[i][1] + float(origin[i])]
    if i < 2 else local_bounds[i]
    for i in range(3)
]
record["accuracy_status"] = (
    "independently graded 8.25/10; R5 asset and master placement marker verified; roof pitch, eaves, "
    "transitions and central monitor are image-estimated; interior remains schematic; long facade "
    "window groups remain simplified"
)
record["independent_grade_file"] = "../audit/walc_refine/independent_grade_r5.md"
record["evidence_file"] = "../audit/walc_refine/independent_grade_r5_reopen.json"
record["asset_sha256"] = asset_hash
if sum(1 for obj in bpy.context.scene.objects if obj.name.startswith("Placement_")) != 69:
    raise RuntimeError("Unexpected master placement marker count")
manifest["detailed_asset_count"] = sum(1 for item in manifest["assets"] if item.get("kind") == "detailed")
manifest["last_master_build"] = "2026-10-25"
verification["master_placement_markers"] = 69
verification["master_scene_object_count"] = len(bpy.context.scene.objects)
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
    "scene_object_count": len(bpy.context.scene.objects),
    "placement_marker_count": 69,
    "manifest_source_object_count": verification["source_asset_object_count"],
    "refreshed": [{
        "id": ASSET_ID,
        "sha256": asset_hash,
        "object_count": len(objects),
        "mesh_count": mesh_count,
        "collection": collection_name,
        "library_path": bpy.path.relpath(str(asset_path)),
        "placement_marker": marker.name,
        "marker_xy_m": [float(marker.location.x), float(marker.location.y)],
        "manifest_xy_m": [float(origin[0]), float(origin[1])],
        "placement_error_m": position_error,
    }],
    "notes": ["WALC R5 library refreshed after its independent grade passed 8.0/10."],
}
write_json(REPORT_PATH, report)
print(json.dumps(report, indent=2, ensure_ascii=False))
