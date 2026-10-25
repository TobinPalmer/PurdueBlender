"""Reload validated building libraries and save the coordinator-owned master."""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "purdue_campus_master.blend"
MODULAR = ROOT / "modular"
ASSET_ID = "massing_france_a_c_rdova_recreational_sports_center_ae69df0"
ASSET_PATH = MODULAR / "buildings" / f"{ASSET_ID}.blend"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
EXPECTED_HASH = "de8de341e0c7fab3304e7d73c0bcfa64f6b1e6a7d1c95097e93e15c8d7003051"

actual_hash = hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()
if actual_hash != EXPECTED_HASH:
    raise RuntimeError(f"CREC asset hash mismatch: {actual_hash}")

bpy.ops.wm.open_mainfile(filepath=str(MASTER))
scene = bpy.context.scene
root_collection = scene.collection
collection = bpy.data.collections.get(COLLECTION_NAME)
if collection is None or collection.library is None:
    raise RuntimeError(f"Master does not link expected collection {COLLECTION_NAME}")
library_path = Path(bpy.path.abspath(collection.library.filepath)).resolve()
if library_path != ASSET_PATH.resolve():
    raise RuntimeError(f"Unexpected CREC library path: {library_path}")

# Explicitly reload the source file so the saved master carries the graded revision.
collection.library.reload()
collection = bpy.data.collections.get(COLLECTION_NAME)
if collection is None or collection.library is None:
    raise RuntimeError("CREC collection vanished during library reload")
if collection not in list(root_collection.children):
    root_collection.children.link(collection)
if sum(1 for child in root_collection.children if child.name == COLLECTION_NAME) != 1:
    raise RuntimeError("CREC collection is linked more than once in the master root")

objects = list(collection.all_objects)
if len(objects) != 199:
    raise RuntimeError(f"Expected 199 CREC collection objects, found {len(objects)}")
crec_validation = json.loads((ROOT / "audit/france_a_cordova_rec_center/validation.json").read_text(encoding="utf-8"))
if crec_validation["blend_sha256"] != actual_hash or crec_validation["collection_object_count"] != len(objects):
    raise RuntimeError("CREC source validation does not match the saved linked library")
# The asset's saved-source vertex check is authoritative for its legacy campus-world bounds;
# linked-object matrix_world values can include master-scene context and are not used here.
bounds = [[crec_validation["campus_world_bounds"][side][i] for side in ("min", "max")]
          for i in range(3)]

manifest_path = MODULAR / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
record = next(a for a in manifest["assets"] if a["id"] == ASSET_ID)
record["objects"] = [o.name for o in objects]
record["object_count"] = len(objects)
record["bounds_world_m"] = bounds
record["exterior_bounds_world_m"] = bounds
record["source_bounds_world_m"] = bounds
record["accuracy_status"] = (
    "independently graded 8.1/10; GIS feature 315 shell and campus-world placement checked; "
    "exact roof-height distribution and interior layout remain approximate/schematic"
)
record["geometry_detail"] = "detailed; legacy campus-world direct-link coordinate contract retained"
record["legacy_source_objects"] = ["France A. Córdova Recreational Sports Center"]
record["evidence_record"] = "../audit/france_a_cordova_rec_center/source_record.json"
record["independent_grade_file"] = "../audit/france_a_cordova_rec_center/independent_grade_r4.md"

def collection_local_matrix(obj, cache):
    if obj in cache:
        return cache[obj]
    matrix = obj.matrix_local.copy()
    if obj.parent is not None:
        matrix = collection_local_matrix(obj.parent, cache) @ matrix
    cache[obj] = matrix
    return matrix

refreshed = [{"id": ASSET_ID, "object_count": len(objects), "hash": actual_hash}]
for asset_id, expected_hash, grade, status, review_path in [
    ("morgan_j_burke_boilermaker_aquatic_center",
     "eec37c28a65fc0c3d48feea6791bb4bbe92b0f218a4f8099689abca078b6aa9a", "7.9/10",
     "independently graded 7.9/10; local GIS outline correspondence verified; roof height and master placement remain unverified",
     "../audit/batchC_boilermaker_aquatic_r1/independent_grade_r8.md"),
    ("neil_armstrong_hall",
     "63c18a8ce250345134399b48dc9eb0f5f5a7563ef3566a5b22145221e7c0145d", "7.6/10",
     "independently graded 7.6/10; roof zones supported by registered imagery; roof extent, facade detail, and atrium circulation remain unresolved",
     "../audit/complete_neil_armstrong/review_r10.md"),
]:
    detail = next(a for a in manifest["assets"] if a["id"] == asset_id)
    path = MODULAR / detail["file"]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != expected_hash:
        raise RuntimeError(f"{asset_id} source hash mismatch: {digest}")
    linked = bpy.data.collections.get(detail["collection"])
    if linked is None or linked.library is None:
        raise RuntimeError(f"Master is missing linked collection {detail['collection']}")
    if Path(bpy.path.abspath(linked.library.filepath)).resolve() != path.resolve():
        raise RuntimeError(f"Unexpected linked path for {asset_id}: {linked.library.filepath}")
    linked.library.reload()
    linked = bpy.data.collections.get(detail["collection"])
    linked_objects = list(linked.all_objects)
    marker = bpy.data.objects.get(f"Placement_{asset_id}")
    if marker is None or marker.instance_collection != linked:
        raise RuntimeError(f"Master placement marker does not instance {asset_id}")
    origin = detail["placement_origin_xy_m"]
    if any(abs(float(marker.location[i]) - origin[i]) > 0.001 for i in range(2)):
        raise RuntimeError(f"Master placement for {asset_id} differs from manifest")
    geometry = [o for o in linked_objects if o.type in {"MESH", "CURVE", "FONT"}]
    cache = {}
    local_points = [collection_local_matrix(o, cache) @ Vector(corner)
                    for o in geometry for corner in o.bound_box]
    if not local_points:
        raise RuntimeError(f"No bounded geometry in {asset_id}")
    local_bounds = [[min(p[i] for p in local_points), max(p[i] for p in local_points)] for i in range(3)]
    world_bounds = [[v + origin[i] for v in local_bounds[i]] if i < 2 else local_bounds[i]
                    for i in range(3)]
    detail["objects"] = [o.name for o in linked_objects]
    detail["object_count"] = len(linked_objects)
    detail["local_bounds_m"] = local_bounds
    detail["bounds_world_m"] = world_bounds
    detail["accuracy_status"] = status
    detail["independent_grade_file"] = review_path
    refreshed.append({"id": asset_id, "object_count": len(linked_objects), "hash": digest,
                      "grade": grade, "local_bounds_m": local_bounds})
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

verification_path = MODULAR / "verification.json"
verification = json.loads(verification_path.read_text(encoding="utf-8"))
verification["source_asset_object_count"] = sum(a.get("object_count", 0) for a in manifest["assets"])
verification["master_scene_object_count"] = len(scene.objects)
verification["master_placement_markers"] = sum(1 for o in scene.objects if o.name.startswith("Placement_"))
if verification["status"] != "PASS" or verification["master_placement_markers"] != 69:
    raise RuntimeError(f"Existing master verification did not pass: {verification}")
verification_path.write_text(json.dumps(verification, indent=2) + "\n", encoding="utf-8")

bpy.ops.wm.save_as_mainfile(filepath=str(MASTER))
print(json.dumps({"status": "PASS", "master": str(MASTER), "asset_id": ASSET_ID,
                  "asset_sha256": actual_hash, "collection_objects": len(objects),
                  "bounds_world_m": bounds, "root_collection_links": 1, "refreshed": refreshed,
                  "verification": verification}, ensure_ascii=False))
