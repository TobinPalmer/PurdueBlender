"""Refresh reviewed buildings and correctly instance the St Thomas local candidate."""
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
REPORT_PATH = ROOT / "audit/master_sync_r26.json"

ASSET_CONFIG = {
    "university_hall": {
        "file": "buildings/university_hall.blend",
        "sha256": "7ed748bb216108115986f276cb5558a445559be75245be95639158221d8538c1",
        "objects": 1377,
        "grade": "audit/university_hall_refine/independent_grade_r7.json",
        "grade_md": "../audit/university_hall_refine/independent_grade_r7.md",
        "evidence": "audit/university_hall_refine/independent_reopen_r7.json",
        "bounds": "evaluated_bounds_local_m_axis_major",
        "score": 8.005,
        "accuracy": (
            "independently graded 8.005/10 (8.0 rounded); R7 asset and master marker verified; roof/tower "
            "details and gallery geometry remain estimates where no registered plans were found; the five "
            "display-column groups and connected stair landings follow public restoration evidence"
        ),
    },
    "wiley_hall": {
        "file": "buildings/wiley_hall.blend",
        "sha256": "8f3e904273ec680811163d8150098aa0f67f55705376df86359b8510cc3a3859",
        "objects": 398,
        "grade": "audit/wiley_hall/independent_grade_r2.json",
        "grade_md": "../audit/wiley_hall/independent_grade_r2.md",
        "evidence": "audit/wiley_hall/independent_reopen_r2.json",
        "bounds": "evaluated_mesh_bounds_local_axis_major_m",
        "score": 8.3,
        "accuracy": (
            "independently graded 8.3/10; R2 asset and existing master marker verified against WILY OBJECTID 290; "
            "shell bbox center agrees with the converted campus GIS ring within about 0.03 m; shell bounds remain "
            "about 10 m short per axis and need a structural wall overlay before any resizing; large lawn/road "
            "context is excluded from Asset_wiley_hall; interiors remain schematic"
        ),
    },
}

ST_ID = "massing_st_thomas_aquinas_5535390"
ST_SHA = "ec8ba6235c6a356ad81ab8b7ad8fcbe3bcc75c4071a310287ea3bb517ad5b7db"
ST_OBJECTS = 1204


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
master_scene = bpy.context.scene
manifest = read_json(MANIFEST_PATH)
verification = read_json(VERIFICATION_PATH)
if verification.get("status") != "PASS":
    raise RuntimeError("Existing modular verification is not PASS")
if verification.get("asset_count") != len(manifest.get("assets", [])):
    raise RuntimeError("Manifest and verification asset counts differ")

refreshed = []
for asset_id, config in ASSET_CONFIG.items():
    record = next((item for item in manifest["assets"] if item["id"] == asset_id), None)
    if record is None or record.get("kind") != "detailed":
        raise RuntimeError(f"Manifest is missing detailed asset {asset_id}")
    asset_path = (MODULAR / config["file"]).resolve()
    asset_hash = hashlib.sha256(asset_path.read_bytes()).hexdigest()
    grade = read_json(ROOT / config["grade"])
    reopen = read_json(ROOT / config["evidence"])
    if asset_hash != config["sha256"] or grade.get("sha256") != asset_hash:
        raise RuntimeError(f"{asset_id} asset and grade hashes differ")
    if float(grade.get("weighted_unrounded_score", grade.get("score", 0))) < 8.0:
        raise RuntimeError(f"{asset_id} does not meet the 8.0 threshold")
    if reopen.get("sha256") != asset_hash:
        raise RuntimeError(f"{asset_id} fresh reopen evidence does not match its asset")
    collection = bpy.data.collections.get(record["collection"])
    marker = bpy.data.objects.get(f"Placement_{asset_id}")
    if collection is None or collection.library is None or marker is None:
        raise RuntimeError(f"Master is missing {asset_id}'s linked collection or marker")
    if Path(bpy.path.abspath(collection.library.filepath)).resolve() != asset_path:
        raise RuntimeError(f"Master link for {asset_id} points to the wrong asset")
    collection.library.reload()
    collection = bpy.data.collections.get(record["collection"])
    marker = bpy.data.objects.get(f"Placement_{asset_id}")
    if collection is None or marker is None or marker.instance_collection != collection:
        raise RuntimeError(f"{asset_id} library reload lost its collection instance")
    if len(collection.all_objects) != config["objects"]:
        raise RuntimeError(f"{asset_id} linked count is {len(collection.all_objects)}, expected {config['objects']}")
    origin = record.get("placement_origin_xy_m")
    if not origin or len(origin) != 2:
        raise RuntimeError(f"{asset_id} manifest origin is missing")
    error = ((float(marker.location.x) - float(origin[0])) ** 2 +
             (float(marker.location.y) - float(origin[1])) ** 2) ** 0.5
    if error > 0.001 or abs(float(marker.location.z)) > 0.001:
        raise RuntimeError(f"{asset_id} marker differs from manifest origin by {error:.6f} m")
    if any(abs(float(value) - 1.0) > 1e-6 for value in marker.scale) or any(abs(float(value)) > 1e-6 for value in marker.rotation_euler):
        raise RuntimeError(f"{asset_id} marker rotation/scale changed")
    if any(child.name == record["collection"] for child in master_scene.collection.children):
        raise RuntimeError(f"{asset_id} source collection is also directly linked to the master scene")
    local_bounds = reopen[config["bounds"]]
    record["objects"] = [obj.name for obj in collection.all_objects]
    record["object_count"] = len(collection.all_objects)
    record["local_bounds_m"] = local_bounds
    record["bounds_world_m"] = world_bounds(local_bounds, origin)
    if asset_id == "university_hall":
        record["exterior_bounds_world_m"] = world_bounds(local_bounds, origin)
    record["accuracy_status"] = config["accuracy"]
    record["independent_grade_file"] = config["grade_md"]
    record["evidence_file"] = "../" + config["evidence"]
    record["asset_sha256"] = asset_hash
    refreshed.append({
        "id": asset_id,
        "sha256": asset_hash,
        "object_count": len(collection.all_objects),
        "collection": record["collection"],
        "library_path": bpy.path.relpath(str(asset_path)),
        "placement_marker": marker.name,
        "marker_xy_m": [float(marker.location.x), float(marker.location.y)],
        "manifest_xy_m": [float(origin[0]), float(origin[1])],
        "placement_error_m": error,
    })

# Convert St Thomas from a direct campus-coordinate massing link into a local
# library instance. Its R3 grade is pending; this is a correctly placed preview,
# not an acceptance or completion claim.
st_record = next((item for item in manifest["assets"] if item["id"] == ST_ID), None)
if st_record is None:
    raise RuntimeError("Manifest is missing the St Thomas Aquinas stable asset ID")
st_path = (MODULAR / st_record["file"]).resolve()
st_hash = hashlib.sha256(st_path.read_bytes()).hexdigest()
st_reopen = read_json(ROOT / "audit/st_thomas_aquinas_5535390/independent_reopen_r3.json")
if st_hash != ST_SHA or st_reopen.get("sha256") != st_hash:
    raise RuntimeError("St Thomas R3 asset does not match its fresh reopen record")
if int(st_reopen.get("object_count", -1)) != ST_OBJECTS or not st_reopen.get("identity_root"):
    raise RuntimeError("St Thomas R3 asset count/root does not match reopen evidence")
st_origin = st_reopen.get("placement_origin_xy_m")
st_grade = read_json(ROOT / "audit/st_thomas_aquinas_5535390/independent_grade_r3.json")
if st_grade.get("sha256") != st_hash:
    raise RuntimeError("St Thomas R3 independent grade is not for the current asset hash")
if not st_origin or len(st_origin) != 2:
    raise RuntimeError("St Thomas R3 campus origin is missing from fresh-reopen evidence")
st_collection = bpy.data.collections.get(st_record["collection"])
if st_collection is None or st_collection.library is None:
    raise RuntimeError("Master is missing the St Thomas linked collection")
if Path(bpy.path.abspath(st_collection.library.filepath)).resolve() != st_path:
    raise RuntimeError("St Thomas master link points to an unexpected source file")
if len(st_collection.all_objects) != ST_OBJECTS:
    raise RuntimeError(f"St Thomas master link has {len(st_collection.all_objects)} objects, expected {ST_OBJECTS}")
if not any(child == st_collection for child in master_scene.collection.children):
    raise RuntimeError("Expected the current St Thomas massing collection to be directly linked for conversion")
st_marker_name = "Placement_" + ST_ID
if bpy.data.objects.get(st_marker_name) is not None:
    raise RuntimeError(f"St Thomas placement marker {st_marker_name} already exists")
master_scene.collection.children.unlink(st_collection)
st_marker = bpy.data.objects.new(st_marker_name, None)
st_marker.empty_display_type = "PLAIN_AXES"
st_marker.empty_display_size = 2.0
st_marker.instance_type = "COLLECTION"
st_marker.instance_collection = st_collection
st_marker.location = (float(st_origin[0]), float(st_origin[1]), 0.0)
st_marker.rotation_euler = (0.0, 0.0, 0.0)
st_marker.scale = (1.0, 1.0, 1.0)
st_marker["asset_id"] = ST_ID
master_scene.collection.objects.link(st_marker)
st_error = ((float(st_marker.location.x) - float(st_origin[0])) ** 2 +
            (float(st_marker.location.y) - float(st_origin[1])) ** 2) ** 0.5
st_local_bounds = st_reopen["bounds_local_axis_major_m"]
st_record["kind"] = "detailed"
st_record["objects"] = [obj.name for obj in st_collection.all_objects]
st_record["object_count"] = len(st_collection.all_objects)
st_record["local_bounds_m"] = st_local_bounds
st_record["bounds_world_m"] = world_bounds(st_local_bounds, st_origin)
st_record["placement_origin_xy_m"] = [float(st_origin[0]), float(st_origin[1])]
st_record["local_coordinates"] = True
st_record["placement_transform"] = "master collection-instance marker translates local geometry to placement_origin_xy_m"
st_record["accuracy_status"] = (
    "R3 preview correctly instanced at the GIS/OSM-derived campus origin; latest independent R3 grade 7.7/10 "
    "(below threshold), R4 refinement needed; GIS/OSM outline IoU 0.922 compares map outlines, not surveyed walls; "
    "roof heights, interior partitions, and room layout remain schematic or unverified"
)
st_record["evidence_file"] = "../audit/st_thomas_aquinas_5535390/independent_reopen_r3.json"
st_record["independent_grade_file"] = "../audit/st_thomas_aquinas_5535390/independent_grade_r3.md"
st_record["previous_grade_file"] = "../audit/st_thomas_aquinas_5535390/independent_grade_r2.md"
st_record["asset_sha256"] = st_hash
placement_count = sum(1 for obj in master_scene.objects if obj.name.startswith("Placement_"))
if placement_count != 70:
    raise RuntimeError(f"Expected 70 placement markers after St Thomas preview conversion; found {placement_count}")
st_refreshed = {
    "id": ST_ID,
    "sha256": st_hash,
    "object_count": len(st_collection.all_objects),
    "collection": st_record["collection"],
    "library_path": bpy.path.relpath(str(st_path)),
    "placement_marker": st_marker.name,
    "marker_xy_m": [float(st_marker.location.x), float(st_marker.location.y)],
    "manifest_xy_m": [float(st_origin[0]), float(st_origin[1])],
    "placement_error_m": st_error,
    "asset_grade_status": "R3_grade_7.7_below_threshold_R4_needed",
}
manifest["detailed_asset_count"] = sum(1 for item in manifest["assets"] if item.get("kind") == "detailed")
verification["detailed_asset_count"] = manifest["detailed_asset_count"]
manifest["last_master_build"] = "2026-10-25"
verification["master_placement_markers"] = placement_count
verification["master_scene_object_count"] = len(master_scene.objects)
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
    "scene_name": master_scene.name,
    "scene_object_count": len(master_scene.objects),
    "placement_marker_count": placement_count,
    "manifest_source_object_count": verification["source_asset_object_count"],
    "refreshed": refreshed + [st_refreshed],
    "notes": [
        "St Thomas is a correctly placed R3 preview; independent score 7.7/10 is below threshold and R4 remains in progress.",
        "Wiley R2 integration is already independently verified in audit/master_sync_r25.json.",
    ],
}
write_json(REPORT_PATH, report)
print(json.dumps(report, indent=2, ensure_ascii=False))
