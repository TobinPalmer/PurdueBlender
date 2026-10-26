"""Refresh the passing Winifred Parker Hall R5 library in the campus master."""
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
REPORT_PATH = ROOT / "audit/master_sync_r28.json"
ASSET_ID = "winifred_parker_hall"
ASSET_FILE = "buildings/winifred_parker_hall.blend"
EXPECTED_SHA = "92fa120794470d93a253d04f35ca0852caea7d05982a5f4e02b285fd914045a9"
EXPECTED_OBJECTS = 582


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def world_bounds(local_bounds, origin):
    return [
        [float(local_bounds[i][0]) + float(origin[i]), float(local_bounds[i][1]) + float(origin[i])]
        if i < 2 else [float(local_bounds[i][0]), float(local_bounds[i][1])]
        for i in range(3)
    ]


if Path(bpy.data.filepath).resolve() != MASTER.resolve():
    raise RuntimeError("Start Blender with purdue_campus_master.blend already loaded")
manifest = read_json(MANIFEST_PATH)
verification = read_json(VERIFICATION_PATH)
record = next((item for item in manifest["assets"] if item["id"] == ASSET_ID), None)
if record is None or record.get("kind") != "detailed":
    raise RuntimeError("Winifred Parker Hall is missing from the detailed manifest")
asset_path = (MODULAR / ASSET_FILE).resolve()
asset_hash = hashlib.sha256(asset_path.read_bytes()).hexdigest()
grade = read_json(ROOT / "audit/winifred_parker_hall/independent_grade_r5.json")
reopen = read_json(ROOT / "audit/winifred_parker_hall/independent_grade_r5_extract.json")
marker_evidence = read_json(ROOT / "audit/winifred_parker_hall/independent_grade_r5_master_marker.json")
if asset_hash != EXPECTED_SHA or grade.get("sha256") != asset_hash or reopen.get("sha256") != asset_hash:
    raise RuntimeError("Winifred R5 asset, grade, and fresh-reopen hashes do not match")
if not grade.get("passed") or float(grade.get("score", 0.0)) < 8.0:
    raise RuntimeError("Winifred R5 has not met the independent 8/10 threshold")
if not reopen.get("fresh_process_reopen") or marker_evidence.get("asset_sha256") != asset_hash:
    raise RuntimeError("Winifred fresh asset or master-marker evidence does not match")
if not marker_evidence.get("fresh_process_read_only_master_reopen"):
    raise RuntimeError("Winifred master placement evidence was not freshly reopened")

scene = bpy.context.scene
collection = bpy.data.collections.get(record["collection"])
marker_name = "Placement_" + ASSET_ID
marker = bpy.data.objects.get(marker_name)
if collection is None or collection.library is None or marker is None:
    raise RuntimeError("Master is missing the Winifred linked library or placement marker")
if Path(bpy.path.abspath(collection.library.filepath)).resolve() != asset_path:
    raise RuntimeError("Winifred master collection points to the wrong source asset")
collection.library.reload()
collection = bpy.data.collections.get(record["collection"])
marker = bpy.data.objects.get(marker_name)
if collection is None or marker is None or marker.instance_collection != collection:
    raise RuntimeError("Reloading the Winifred library lost its collection instance")
if len(collection.all_objects) != EXPECTED_OBJECTS:
    raise RuntimeError(f"Winifred linked count is {len(collection.all_objects)}, expected {EXPECTED_OBJECTS}")
origin = record.get("placement_origin_xy_m")
if not origin or len(origin) != 2:
    raise RuntimeError("Winifred manifest placement origin is missing")
position_error = ((float(marker.location.x) - float(origin[0])) ** 2 +
                  (float(marker.location.y) - float(origin[1])) ** 2) ** 0.5
if position_error > 0.001 or abs(float(marker.location.z)) > 0.001:
    raise RuntimeError(f"Winifred master marker differs from manifest origin by {position_error:.6f} m")
if any(abs(float(value) - 1.0) > 1e-6 for value in marker.scale) or any(
    abs(float(value)) > 1e-6 for value in marker.rotation_euler
):
    raise RuntimeError("Winifred master marker rotation or scale is not identity")
if any(child.name == record["collection"] for child in scene.collection.children):
    raise RuntimeError("Winifred collection is linked directly to the scene in addition to its marker")

local_bounds = reopen["aggregate_mesh_bounds_local"]
record["objects"] = [obj.name for obj in collection.all_objects]
record["object_count"] = EXPECTED_OBJECTS
record["local_bounds_m"] = local_bounds
record["bounds_world_m"] = world_bounds(local_bounds, origin)
record["asset_sha256"] = asset_hash
record["independent_grade_score"] = float(grade["score"])
record["independent_grade_file"] = "../audit/winifred_parker_hall/independent_grade_r5.md"
record["evidence_file"] = "../audit/winifred_parker_hall/independent_grade_r5_extract.json"
record["accuracy_status"] = (
    "R5 independently graded 8.05/10; fresh exact-file and read-only master checks pass; the main shell outline "
    "matches Purdue GIS FID 879 and 2023 orthophoto roof edges, but the GIS ring is not a surveyed wall line and "
    "its Shape__Area field conflicts with its returned ring area; roof/floor height fields are ambiguous, interiors "
    "and materials remain schematic"
)

manifest["detailed_asset_count"] = sum(1 for item in manifest["assets"] if item.get("kind") == "detailed")
verification["detailed_asset_count"] = manifest["detailed_asset_count"]
verification["master_placement_markers"] = sum(1 for obj in scene.objects if obj.name.startswith("Placement_"))
verification["master_scene_object_count"] = len(scene.objects)
verification["source_asset_object_count"] = sum(int(item.get("object_count", 0)) for item in manifest["assets"])
verification["status"] = "PASS"
verification["errors"] = []
if verification["master_placement_markers"] != 70:
    raise RuntimeError(f"Expected 70 placement markers, found {verification['master_placement_markers']}")
if verification["asset_count"] != len(manifest["assets"]):
    raise RuntimeError("Manifest and verification asset counts differ")
if verification["building_count"] != verification["asset_count"] - 1:
    raise RuntimeError("Verification building count is inconsistent")

bpy.ops.wm.save_as_mainfile(filepath=str(MASTER))
write_json(MANIFEST_PATH, manifest)
write_json(VERIFICATION_PATH, verification)
report = read_json(ROOT / "audit/master_sync_r27.json")
report["status"] = "SAVED_PENDING_FRESH_REOPEN"
report["master"] = str(MASTER)
report["master_reopened_after_save"] = False
report["scene_name"] = scene.name
report["scene_object_count"] = len(scene.objects)
report["placement_marker_count"] = verification["master_placement_markers"]
report["manifest_source_object_count"] = verification["source_asset_object_count"]
report["refreshed"].append({
    "id": ASSET_ID,
    "sha256": asset_hash,
    "object_count": EXPECTED_OBJECTS,
    "collection": record["collection"],
    "library_path": bpy.path.relpath(str(asset_path)),
    "placement_marker": marker_name,
    "marker_xy_m": [float(marker.location.x), float(marker.location.y)],
    "manifest_xy_m": [float(origin[0]), float(origin[1])],
    "placement_error_m": position_error,
    "grade": float(grade["score"]),
})
report["notes"].append("Winifred Parker Hall R5 independently passes at 8.05/10; the master link and placement were refreshed.")
write_json(REPORT_PATH, report)
print(json.dumps(report, indent=2, ensure_ascii=False))
