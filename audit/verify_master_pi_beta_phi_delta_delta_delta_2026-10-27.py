"""Fresh-open verification for two recent Greek-house master integrations."""
import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(bpy.data.filepath).resolve().parent
MANIFEST = json.loads((ROOT / "modular" / "manifest.json").read_text(encoding="utf-8"))
IDS = ["massing_house_301838781_891384f", "massing_house_301841333_affe21e"]
records = {a["id"]: a for a in MANIFEST["assets"]}
scene = bpy.context.scene
errors = []
results = []

def local_matrix(obj, cache):
    if obj in cache:
        return cache[obj]
    matrix = obj.matrix_local.copy()
    if obj.parent is not None:
        matrix = local_matrix(obj.parent, cache) @ matrix
    cache[obj] = matrix
    return matrix

for asset_id in IDS:
    record = records.get(asset_id)
    if record is None:
        errors.append(f"{asset_id}: manifest row missing")
        continue
    asset_path = (ROOT / "modular" / record["file"]).resolve()
    actual_sha = hashlib.sha256(asset_path.read_bytes()).hexdigest() if asset_path.is_file() else None
    if actual_sha != record.get("sha256"):
        errors.append(f"{asset_id}: asset SHA mismatch {actual_sha}")
    if record.get("kind") != "detailed":
        errors.append(f"{asset_id}: manifest kind is not detailed")
    collection = bpy.data.collections.get(record["collection"])
    marker = bpy.data.objects.get(f"Placement_{asset_id}")
    if collection is None or marker is None:
        errors.append(f"{asset_id}: collection or placement marker missing")
        continue
    linked_path = Path(bpy.path.abspath(collection.library.filepath)).resolve() if collection.library else None
    if linked_path != asset_path:
        errors.append(f"{asset_id}: linked path mismatch {linked_path}")
    if marker.instance_collection != collection or marker.instance_type != "COLLECTION":
        errors.append(f"{asset_id}: marker references the wrong collection/instance type")
    origin = record.get("placement_origin_xy_m")
    if not origin or max(abs(float(marker.location[i]) - float(origin[i])) for i in range(2)) > 0.001:
        errors.append(f"{asset_id}: marker coordinate mismatch")
    direct_links = sum(child == collection for child in scene.collection.children)
    if direct_links:
        errors.append(f"{asset_id}: source collection remains directly linked {direct_links} time(s)")
    objects = list(collection.all_objects)
    if len(objects) != record.get("object_count"):
        errors.append(f"{asset_id}: object count mismatch {len(objects)} != {record.get('object_count')}")
    cache = {}
    points = [local_matrix(obj, cache) @ Vector(corner)
              for obj in objects if obj.type == "MESH" for corner in obj.bound_box]
    points = [Vector((p.x + marker.location.x, p.y + marker.location.y, p.z)) for p in points]
    actual_bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)] if points else None
    expected_bounds = record.get("bounds_world_m")
    max_bounds_error = max(abs(actual_bounds[i][j] - expected_bounds[i][j])
                           for i in range(3) for j in range(2)) if actual_bounds and expected_bounds else None
    if max_bounds_error is None or max_bounds_error > 0.01:
        errors.append(f"{asset_id}: world-bound error {max_bounds_error}")
    results.append({
        "id": asset_id,
        "score": record.get("independent_grade_score"),
        "sha256": actual_sha,
        "linked_path": str(linked_path) if linked_path else None,
        "placement_xy_m": [float(marker.location.x), float(marker.location.y)],
        "object_count": len(objects),
        "mesh_object_count": sum(obj.type == "MESH" for obj in objects),
        "direct_collection_links": direct_links,
        "actual_bounds_world_m": actual_bounds,
        "expected_bounds_world_m": expected_bounds,
        "max_world_bounds_error_m": max_bounds_error,
    })

report = {
    "status": "PASS" if not errors else "FAIL",
    "master_file": str(Path(bpy.data.filepath).resolve()),
    "fresh_open_blender_version": bpy.app.version_string,
    "scene": scene.name,
    "scene_object_count": len(scene.objects),
    "checked_buildings": len(results),
    "results": results,
    "errors": errors,
}
out = ROOT / "audit" / "master_integration_pi_beta_phi_delta_delta_delta_2026-10-27.json"
out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
if errors:
    raise RuntimeError("Greek-house master verification failed")
