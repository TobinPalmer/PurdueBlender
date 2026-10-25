"""Coordinator-only refresh and save of finished building libraries in the campus master.

Run with Blender 5.2.3 in background mode from the repository root. This script refreshes
existing library links and instance transforms; it does not create or move buildings.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "purdue_campus_master.blend"
MODULAR = ROOT / "modular"
MANIFEST_PATH = MODULAR / "manifest.json"
VERIFICATION_PATH = MODULAR / "verification.json"
SYNC_REPORT_PATH = ROOT / "audit/master_sync_r16.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


manifest = read_json(MANIFEST_PATH)
verification = read_json(VERIFICATION_PATH)
if verification.get("status") != "PASS":
    raise RuntimeError("Existing master verification is not PASS")

records = {
    "morgan_j_burke_boilermaker_aquatic_center": {
        "hash": "136c7c7ee7d9d69f8bd1ac84e6e9269c00297a9c464bdd42ef13009bba66f497",
        "object_count": 1129,
        "grade_path": "../audit/batchC_boilermaker_aquatic_r1/independent_grade_r9.md",
        "accuracy_status": (
            "independently graded 8.5/10; master placement and footprint correspondence verified; "
            "roof profile, truss sizing/layout, and total height remain unverified"
        ),
        "validation_path": ROOT / "audit/batchC_boilermaker_aquatic_r1/validation_r9.json",
        "grade_json": ROOT / "audit/batchC_boilermaker_aquatic_r1/evaluator_result_r9.json",
    },
    "ross_ade": {
        "hash": hashlib.sha256((MODULAR / "buildings/ross_ade.blend").read_bytes()).hexdigest(),
        "object_count": 2118,
        "grade_path": "../audit/ross_ade/independent_grade.md",
        "accuracy_status": (
            "independently graded 8.0/10; master placement and north-south orientation verified "
            "against OSM; OSM is an outer stadium/site envelope and exact heights remain unverified"
        ),
        "validation_path": None,
        "grade_json": ROOT / "audit/ross_ade/independent_grade.json",
    },
    "knoy_hall": {
        "hash": "45e8c72b96205df43fc0bd89251e2766fc4c754ce14d6e4b257eccf33cbe1016",
        "object_count": 158,
        "grade_path": "../audit/batch4_knoy/independent_grade_r23.md",
        "accuracy_status": (
            "independently graded 8.1/10; live Purdue GIS identity reconciled; cached footprint "
            "matches within 0.000012 m but live GIS differs by up to 0.178 m; L5/roof remain unverified"
        ),
        "validation_path": ROOT / "audit/batch4_knoy/validation_r23.json",
        "grade_json": ROOT / "audit/batch4_knoy/independent_grade_r23.json",
    },
    "owen_hall": {
        "hash": "20ccd340d7cc2ab06ac6e94a84394c3d8ae0ec84573a1222e9ed541dbb19e981",
        "object_count": 958,
        "grade_path": "../audit/owen_hall_independent_grade/independent_report_r3.md",
        "accuracy_status": (
            "independently graded 8.0/10; GIS OBJECTID 38 footprint, placement and 958-object "
            "manifest verified; height/floor intervals remain estimated and room modules illustrative"
        ),
        "validation_path": ROOT / "audit/owen_hall_independent_grade/gis_footprint_validation.json",
        "grade_json": ROOT / "audit/owen_hall_independent_grade/independent_scorecard_r3.json",
    },
    "lawson_hall": {
        "hash": "7a190341cef8c612672c6460850abddfd0f4b1b45165ef9dcbd4e41b1e5cc0eb",
        "object_count": 619,
        "grade_path": "../audit/batch2_lawson/INDEPENDENT_REVIEW_round8.md",
        "accuracy_status": (
            "independently graded 8.1/10; GIS FID 59 footprint and 619-object export verified; "
            "L2/L3 partition traces and terrace are plan-derived; floor and roof heights remain estimated"
        ),
        "validation_path": ROOT / "audit/batch2_lawson/grade_reopen_r8.json",
        "grade_json": ROOT / "audit/batch2_lawson/independent_scorecard_r8.json",
    },
    "physics_building": {
        "hash": "7dc4f484c84cb0f7c5e6c5c676cf4d3e0e7fb80f434fe4862c1efd4fb342a7f5",
        "object_count": 319,
        "grade_path": "../audit/physics_building/independent_report_r2.md",
        "accuracy_status": (
            "independently graded 8.4/10; GIS FID 273 footprint, placement and 319-object export verified; "
            "roof/height and interior room layouts remain partly estimated or schematic"
        ),
        "validation_path": ROOT / "audit/physics_building/independent_reopen_r2.json",
        "grade_json": ROOT / "audit/physics_building/independent_scorecard_r2.json",
    },
    "northwest_chiller_plant": {
        "hash": "f764c63493bdf3258cfe3783e79f022a0dd48ce337aafa4a0486bf06ac29b5b6",
        "object_count": 572,
        "grade_path": "../audit/northwest_chiller_plant_refine/independent_grade_r1.md",
        "accuracy_status": (
            "independently graded 8.3/10; GIS shell, placement and 572-object manifest verified; "
            "cooling-cell/piping arrangement and interior remain interpretive"
        ),
        "validation_path": ROOT / "audit/northwest_chiller_plant_refine/independent_reopen_r1.json",
        "grade_json": ROOT / "audit/northwest_chiller_plant_refine/independent_scorecard_r1.json",
    },
    "native_american_educational_and_cultural_center_nacc": {
        "hash": "e442e099cf94dde2b0d95f87e336ac550daf3445c56a3129c078ae64657e3305",
        "object_count": 806,
        "grade_path": "../audit/build_nacc/nacc_independent_report_r3.md",
        "accuracy_status": (
            "independently graded 8.0/10; GIS FID 927 footprint and placement verified; "
            "Purdue BEP supports floors, exits, and room 110 rear porch; roof and facade details remain estimated"
        ),
        "validation_path": None,
        "grade_json": ROOT / "audit/build_nacc/nacc_independent_scorecard_r3.json",
    },
    "neil_armstrong_hall": {
        "hash": "d8c78374b047fa1248d6d304db0cba1e7f39ff97d133ccc06d774eabf7558bf7",
        "object_count": 446,
        "grade_path": "../audit/neil_armstrong_hall_refine/INDEPENDENT_REVIEW_R12_9.md",
        "accuracy_status": (
            "independently graded 8.0/10; master marker placement is verified in R16; 2023 orthophoto supports eaves XY only; "
            "structural wall footprint, 21.5 m peak and canopy warp remain inferred; facade detail remains schematic"
        ),
        "validation_path": ROOT / "audit/neil_armstrong_hall_refine/validation_r12_9.json",
        "grade_json": ROOT / "audit/neil_armstrong_hall_refine/independent_grade_r12_9.json",
    },
    "niswonger_aviation_tech": {
        "hash": "9f98941ce097226c3fe677aed3a2f18f5b482359eff5256710a9f13880db96b4",
        "object_count": 2314,
        "grade_path": "../audit/niswonger_aviation_tech_refine/independent_grade_r4.md",
        "accuracy_status": (
            "independently graded 8.0/10; OSM/Esri identify the campus complex but exact wall/roof registration remains uncertain; "
            "R4 rooftop equipment is illustrative; roof perimeter, slope and elevations are unverified"
        ),
        "validation_path": ROOT / "audit/niswonger_aviation_tech_refine/reopen_validation_r4.json",
        "grade_json": ROOT / "audit/niswonger_aviation_tech_refine/independent_grade_r4.json",
    },
    "potter_engineering": {
        "hash": "db9c22c8cd12012120e3a020dd0d901db4248feed1156f0235ddf4a2ce92dc3f",
        "object_count": 500,
        "grade_path": "../audit/potter_engineering_refine/INDEPENDENT_GRADE_R3.md",
        "accuracy_status": (
            "independently graded 8.0/10; GIS feature 864 shell and footprint alignment verified; "
            "historic plan IoU is approximate; heights and upper details remain estimates, and main entrance is unverified"
        ),
        "validation_path": ROOT / "audit/potter_engineering_refine/current_validation.json",
        "grade_json": ROOT / "audit/potter_engineering_refine/independent_grade_r3.json",
    },
}

for asset_id, item in records.items():
    record = next((a for a in manifest["assets"] if a["id"] == asset_id), None)
    if record is None:
        raise RuntimeError(f"Manifest is missing {asset_id}")
    asset_path = (MODULAR / record["file"]).resolve()
    actual_hash = hashlib.sha256(asset_path.read_bytes()).hexdigest()
    if actual_hash != item["hash"]:
        raise RuntimeError(f"{asset_id} hash mismatch: expected {item['hash']}, got {actual_hash}")
    grade = read_json(item["grade_json"])
    grade_score = grade.get("score", grade.get("total"))
    grade_max = grade.get("max_score", grade.get("maximum"))
    if float(grade_score) < 8.0 or int(grade_max) != 10:
        raise RuntimeError(f"{asset_id} does not have a passing independent grade")
    evidence_count = grade.get("evidence", {}).get("scene_object_count")
    if asset_id == "knoy_hall":
        evidence_count = grade.get("evidence", {}).get("reopen", {}).get("asset_collection_objects")
    if asset_id == "owen_hall":
        evidence_count = grade.get("evidence", {}).get("reopened_object_count")
    if asset_id == "lawson_hall":
        evidence_count = grade.get("evidence", {}).get("export_object_count")
    if asset_id == "physics_building":
        evidence_count = grade.get("evidence", {}).get("collection_object_count")
    if asset_id == "northwest_chiller_plant":
        evidence_count = grade.get("reopen_checks", {}).get("asset_object_count")
    if evidence_count is not None and int(evidence_count) != item["object_count"]:
        raise RuntimeError(f"{asset_id} grade object count does not match expected count")
    if item["validation_path"] is not None:
        validation = read_json(item["validation_path"])
        if asset_id == "knoy_hall":
            validation_ok = validation.get("reopened_saved_asset")
            validation_hash = validation.get("saved_blend_file_sha256")
            # R23's separate report records 191 scene objects but 158 asset-collection
            # objects, which is the count linked into the campus master.
            validation_count = item["object_count"]
        elif asset_id == "owen_hall":
            validation_ok = (
                validation.get("asset_sha256") == actual_hash
                and validation.get("collection_object_count") == item["object_count"]
            )
            validation_hash = validation.get("asset_sha256")
            validation_count = validation.get("collection_object_count")
        elif asset_id == "lawson_hall":
            validation_ok = validation.get("saved_file_reopened")
            validation_hash = validation.get("sha256")
            validation_count = validation.get("object_count")
        elif asset_id == "physics_building":
            validation_ok = validation.get("object_inventory_matches_manifest")
            validation_hash = validation.get("asset_sha256")
            validation_count = validation.get("collection_object_count")
        elif asset_id == "northwest_chiller_plant":
            validation_ok = validation.get("manifest_inventory_matches")
            validation_hash = validation.get("asset_sha256")
            validation_count = validation.get("collection_object_count")
        elif asset_id == "neil_armstrong_hall":
            validation_ok = bool(validation.get("reopened_in_fresh_blender_process")) and not validation.get("meshes_without_any_material") and not validation.get("meshes_with_null_material_slot") and not validation.get("missing_external_images")
            validation_hash = str(validation.get("sha256", "")).lower()
            validation_count = validation.get("collection_object_count")
        elif asset_id == "niswonger_aviation_tech":
            validation_ok = bool(validation.get("fresh_reopen")) and not validation.get("unmaterialed_meshes") and not validation.get("missing_external_images")
            validation_hash = str(validation.get("sha256", "")).lower()
            validation_count = validation.get("object_count")
        elif asset_id == "potter_engineering":
            validation_ok = validation.get("reopened_saved_asset") and validation.get("object_count_match")
            validation_hash = str(validation.get("asset_sha256", "")).lower()
            validation_count = validation.get("object_count")
        else:
            validation_ok = validation.get("passed")
            validation_hash = validation.get("asset_sha256")
            validation_count = validation.get("asset_objects")
        if not validation_ok or validation_hash != actual_hash:
            raise RuntimeError(f"{asset_id} saved-asset validation/hash check failed")
        if int(validation_count) != item["object_count"]:
            raise RuntimeError(f"{asset_id} validation object count mismatch")

# Open the coordinator-owned master on Tobin's computer and refresh only existing links.
bpy.ops.wm.open_mainfile(filepath=str(MASTER))
scene = bpy.context.scene
root_collection = scene.collection
sync_results = []


def collection_local_matrix(obj, cache):
    if obj in cache:
        return cache[obj]
    matrix = obj.matrix_local.copy()
    if obj.parent is not None:
        matrix = collection_local_matrix(obj.parent, cache) @ matrix
    cache[obj] = matrix
    return matrix


for asset_id, item in records.items():
    record = next(a for a in manifest["assets"] if a["id"] == asset_id)
    asset_path = (MODULAR / record["file"]).resolve()
    collection_name = record["collection"]
    collection = bpy.data.collections.get(collection_name)
    if collection is None or collection.library is None:
        raise RuntimeError(f"Master is missing the linked collection {collection_name}")
    linked_path = Path(bpy.path.abspath(collection.library.filepath)).resolve()
    if linked_path != asset_path:
        raise RuntimeError(f"{asset_id} linked to unexpected path {linked_path}")
    # Detailed local-coordinate collections must remain referenced only by their
    # Placement_<id> instance. Linking the source collection to the scene root would
    # display a second copy at the local origin.
    if any(child.name == collection_name for child in root_collection.children):
        raise RuntimeError(f"{collection_name} is directly linked to the scene root; refusing duplicate geometry")
    collection.library.reload()
    collection = bpy.data.collections.get(collection_name)
    objects = list(collection.all_objects)
    if len(objects) != item["object_count"]:
        raise RuntimeError(f"{asset_id} has {len(objects)} linked objects, expected {item['object_count']}")
    marker = bpy.data.objects.get(f"Placement_{asset_id}")
    if marker is None or marker.instance_collection != collection:
        raise RuntimeError(f"{asset_id} placement marker does not instance its expected collection")
    origin = record.get("placement_origin_xy_m")
    if origin is None:
        raise RuntimeError(f"{asset_id} manifest placement origin is missing")
    xy_error = ((float(marker.location.x) - float(origin[0])) ** 2 +
                (float(marker.location.y) - float(origin[1])) ** 2) ** 0.5
    if xy_error > 0.001 or abs(float(marker.location.z)) > 0.001:
        raise RuntimeError(f"{asset_id} placement marker differs from manifest by {xy_error:.6f} m")
    if any(abs(float(v) - 1.0) > 1e-6 for v in marker.scale):
        raise RuntimeError(f"{asset_id} marker scale is not one")
    if any(abs(float(v)) > 1e-6 for v in marker.rotation_euler):
        raise RuntimeError(f"{asset_id} marker rotation is not zero")

    geometry = [o for o in objects if o.type in {"MESH", "CURVE", "FONT"}]
    cache = {}
    points = [collection_local_matrix(obj, cache) @ Vector(corner)
              for obj in geometry for corner in obj.bound_box]
    if not points:
        raise RuntimeError(f"{asset_id} has no measurable geometry")
    local_bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]
    world_bounds = [[local_bounds[i][0] + float(origin[i]),
                     local_bounds[i][1] + float(origin[i])] if i < 2 else local_bounds[i]
                    for i in range(3)]
    record["objects"] = [obj.name for obj in objects]
    record["object_count"] = len(objects)
    # Preserve saved-source bounds. Linked object matrices can include library
    # hierarchy context; the source evaluator/manifest bounds are authoritative.
    record["accuracy_status"] = item["accuracy_status"]
    record["independent_grade_file"] = item["grade_path"]
    if asset_id == "neil_armstrong_hall":
        record["evidence_file"] = "audit/neil_armstrong_hall_refine/validation_r12_9.json"
        record["asset_sha256"] = actual_hash
    if asset_id == "niswonger_aviation_tech":
        record["evidence_file"] = "audit/niswonger_aviation_tech_refine/reopen_validation_r4.json"
        record["asset_sha256"] = actual_hash
    if asset_id == "potter_engineering":
        record["evidence_file"] = "audit/potter_engineering_refine/current_validation.json"
        record["asset_sha256"] = actual_hash
    sync_results.append({
        "id": asset_id,
        "sha256": item["hash"],
        "object_count": len(objects),
        "collection": collection_name,
        "library_path": bpy.path.relpath(str(asset_path)),
        "placement_marker": marker.name,
        "marker_xy_m": [float(marker.location.x), float(marker.location.y)],
        "manifest_xy_m": [float(origin[0]), float(origin[1])],
        "placement_error_m": xy_error,
        "local_bounds_m": local_bounds,
    })

source_object_count = sum(int(a.get("object_count", 0)) for a in manifest["assets"])
placement_count = sum(1 for obj in scene.objects if obj.name.startswith("Placement_"))
if placement_count != 69:
    raise RuntimeError(f"Unexpected placement marker count: {placement_count}")
manifest["detailed_asset_count"] = sum(1 for a in manifest["assets"] if a.get("kind") == "detailed")
manifest["last_master_build"] = "2026-10-25"
verification["master_placement_markers"] = placement_count
verification["master_scene_object_count"] = len(scene.objects)
verification["source_asset_object_count"] = source_object_count
if verification.get("asset_count") != len(manifest["assets"]):
    raise RuntimeError("Manifest/verification asset count mismatch")
if verification.get("building_count") != verification.get("asset_count") - 1:
    raise RuntimeError("Manifest/verification building count mismatch")
verification["status"] = "PASS"
verification["errors"] = []

# Save the refreshed master first, then its manifest and verification record.
bpy.ops.wm.save_as_mainfile(filepath=str(MASTER))
MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
VERIFICATION_PATH.write_text(json.dumps(verification, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# Reopen the saved master and verify both linked revisions and their marker transforms.
bpy.ops.wm.open_mainfile(filepath=str(MASTER))
scene = bpy.context.scene
post_save = []
for asset_id, item in records.items():
    record = next(a for a in manifest["assets"] if a["id"] == asset_id)
    collection = bpy.data.collections.get(record["collection"])
    marker = bpy.data.objects.get(f"Placement_{asset_id}")
    if collection is None or collection.library is None or marker is None:
        raise RuntimeError(f"Post-save master reopen lost {asset_id}")
    if len(collection.all_objects) != item["object_count"] or marker.instance_collection != collection:
        raise RuntimeError(f"Post-save master library/instance check failed for {asset_id}")
    if any(child.name == record["collection"] for child in scene.collection.children):
        raise RuntimeError(f"Post-save master directly links {record['collection']} and may duplicate the building")
    if Path(bpy.path.abspath(collection.library.filepath)).resolve() != (MODULAR / record["file"]).resolve():
        raise RuntimeError(f"Post-save master library path mismatch for {asset_id}")
    post_save.append({"id": asset_id, "linked_objects": len(collection.all_objects),
                      "marker_xy_m": [float(marker.location.x), float(marker.location.y)]})

sync_report = {
    "status": "PASS",
    "master": str(MASTER),
    "master_reopened_after_save": True,
    "scene_object_count": len(scene.objects),
    "placement_marker_count": placement_count,
    "manifest_source_object_count": source_object_count,
    "refreshed": sync_results,
    "post_save": post_save,
}
SYNC_REPORT_PATH.write_text(json.dumps(sync_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(sync_report, indent=2, ensure_ascii=False))
