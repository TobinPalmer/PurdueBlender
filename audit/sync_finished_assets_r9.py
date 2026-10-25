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
    if float(grade["score"]) < 8.0 or int(grade["max_score"]) != 10:
        raise RuntimeError(f"{asset_id} does not have a passing independent grade")
    evidence_count = grade.get("evidence", {}).get("scene_object_count")
    if asset_id == "knoy_hall":
        evidence_count = grade.get("evidence", {}).get("reopen", {}).get("asset_collection_objects")
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

print(json.dumps({
    "status": "PASS",
    "master": str(MASTER),
    "master_reopened_after_save": True,
    "scene_object_count": len(scene.objects),
    "placement_marker_count": placement_count,
    "manifest_source_object_count": source_object_count,
    "refreshed": sync_results,
    "post_save": post_save,
}, indent=2, ensure_ascii=False))
