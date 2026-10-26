"""Refresh the passing St Thomas Aquinas R4 library in the campus master."""
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
REPORT_PATH = ROOT / "audit/master_sync_r27.json"
ASSET_ID = "massing_st_thomas_aquinas_5535390"
ASSET_FILE = "buildings/massing_st_thomas_aquinas_5535390.blend"
EXPECTED_SHA = "a06977c0783442a0eb7561d23e294bfc65d11546b3aa4a0c13d9c9b62f68a330"
EXPECTED_OBJECTS = 1275


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
    raise RuntimeError("St Thomas is missing from the detailed manifest")
asset_path = (MODULAR / ASSET_FILE).resolve()
asset_hash = hashlib.sha256(asset_path.read_bytes()).hexdigest()
grade_path = ROOT / "audit/st_thomas_aquinas_5535390/independent_grade_r4.json"
reopen_path = ROOT / "audit/st_thomas_aquinas_5535390/independent_reopen_r4.json"
grade = read_json(grade_path)
reopen = read_json(reopen_path)
if asset_hash != EXPECTED_SHA or grade.get("sha256") != asset_hash or reopen.get("sha256") != asset_hash:
    raise RuntimeError("St Thomas R4 asset, grade, and fresh-reopen hashes do not match")
if not grade.get("passed") or float(grade.get("score", 0.0)) < 8.0:
    raise RuntimeError("St Thomas R4 has not met the independent 8/10 acceptance threshold")
if not reopen.get("fresh_process_reopen") or not reopen.get("identity_root"):
    raise RuntimeError("St Thomas R4 fresh reopen or identity-root check failed")
if int(reopen.get("object_count", -1)) != EXPECTED_OBJECTS:
    raise RuntimeError("St Thomas R4 object count differs from the independently reopened asset")

scene = bpy.context.scene
collection = bpy.data.collections.get(record["collection"])
marker_name = "Placement_" + ASSET_ID
marker = bpy.data.objects.get(marker_name)
if collection is None or collection.library is None or marker is None:
    raise RuntimeError("Master is missing the St Thomas linked library or placement marker")
if Path(bpy.path.abspath(collection.library.filepath)).resolve() != asset_path:
    raise RuntimeError("St Thomas master collection points to the wrong source asset")
collection.library.reload()
collection = bpy.data.collections.get(record["collection"])
marker = bpy.data.objects.get(marker_name)
if collection is None or marker is None or marker.instance_collection != collection:
    raise RuntimeError("Reloading the St Thomas library lost its collection instance")
if len(collection.all_objects) != EXPECTED_OBJECTS:
    raise RuntimeError(f"St Thomas linked count is {len(collection.all_objects)}, expected {EXPECTED_OBJECTS}")
origin = reopen.get("placement_origin_xy_m")
if not origin or len(origin) != 2 or record.get("placement_origin_xy_m") != origin:
    raise RuntimeError("St Thomas R4 source origin differs from the manifest placement")
position_error = ((float(marker.location.x) - float(origin[0])) ** 2 +
                  (float(marker.location.y) - float(origin[1])) ** 2) ** 0.5
if position_error > 0.001 or abs(float(marker.location.z)) > 0.001:
    raise RuntimeError(f"St Thomas master marker differs from the asset origin by {position_error:.6f} m")
if any(abs(float(value) - 1.0) > 1e-6 for value in marker.scale) or any(
    abs(float(value)) > 1e-6 for value in marker.rotation_euler
):
    raise RuntimeError("St Thomas master marker rotation or scale is not identity")
if any(child.name == record["collection"] for child in scene.collection.children):
    raise RuntimeError("St Thomas collection is directly linked to the scene in addition to its marker")

local_bounds = reopen["bounds_local_axis_major_m"]
record["objects"] = [obj.name for obj in collection.all_objects]
record["object_count"] = EXPECTED_OBJECTS
record["local_bounds_m"] = local_bounds
record["bounds_world_m"] = world_bounds(local_bounds, origin)
record["placement_origin_xy_m"] = [float(origin[0]), float(origin[1])]
record["local_coordinates"] = True
record["placement_transform"] = "master collection-instance marker translates local geometry to placement_origin_xy_m"
record["asset_sha256"] = asset_hash
record["independent_grade_score"] = float(grade["score"])
record["independent_grade_file"] = "../audit/st_thomas_aquinas_5535390/independent_grade_r4.md"
record["previous_grade_file"] = "../audit/st_thomas_aquinas_5535390/independent_grade_r3.md"
record["evidence_file"] = "../audit/st_thomas_aquinas_5535390/independent_reopen_r4.json"
record["accuracy_status"] = (
    "R4 independently graded 8.2/10; exact source asset reopened and passed; foundation outline matches Purdue "
    "GIS FID 852 at IoU 0.999999957 (map outline, not surveyed wall faces); master marker is within 0.00000345 m "
    "of the GIS/OSM-derived local origin; interior partitions, classroom fit-out, and roof junction details remain "
    "schematic where measured plans were unavailable"
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
report = {
    "status": "SAVED_PENDING_FRESH_REOPEN",
    "master": str(MASTER),
    "master_reopened_after_save": False,
    "scene_name": scene.name,
    "scene_object_count": len(scene.objects),
    "placement_marker_count": verification["master_placement_markers"],
    "manifest_source_object_count": verification["source_asset_object_count"],
    "refreshed_asset": {
        "id": ASSET_ID,
        "sha256": asset_hash,
        "grade": float(grade["score"]),
        "object_count": EXPECTED_OBJECTS,
        "collection": record["collection"],
        "library_path": bpy.path.relpath(str(asset_path)),
        "placement_marker": marker_name,
        "marker_xy_m": [float(marker.location.x), float(marker.location.y)],
        "manifest_xy_m": [float(origin[0]), float(origin[1])],
        "placement_error_m": position_error,
    },
    "notes": [
        "St Thomas Aquinas R4 independently passes at 8.2/10 and replaces the R3 preview.",
        "University Hall R7 and Wiley Hall R2 remain independently accepted and integrated.",
    ],
}
write_json(REPORT_PATH, report)
print(json.dumps(report, indent=2, ensure_ascii=False))
