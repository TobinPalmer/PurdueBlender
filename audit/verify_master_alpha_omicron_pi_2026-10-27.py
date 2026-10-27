"""Fresh-open verification for the Alpha Omicron Pi master integration."""
import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(bpy.data.filepath).resolve().parent
ASSET_ID = "massing_house_970455277_a3fb72a"
MANIFEST = json.loads((ROOT / "modular" / "manifest.json").read_text(encoding="utf-8"))
record = next((asset for asset in MANIFEST["assets"] if asset["id"] == ASSET_ID), None)
scene = bpy.context.scene
errors = []

if record is None:
    raise RuntimeError(f"Missing {ASSET_ID} manifest row")
asset_path = (ROOT / "modular" / record["file"]).resolve()
actual_sha = hashlib.sha256(asset_path.read_bytes()).hexdigest() if asset_path.is_file() else None
if record.get("kind") != "detailed":
    errors.append("Manifest kind is not detailed")
if actual_sha != record.get("sha256"):
    errors.append(f"Asset SHA mismatch: {actual_sha}")
collection = bpy.data.collections.get(record["collection"])
marker = bpy.data.objects.get(f"Placement_{ASSET_ID}")
if collection is None or marker is None:
    errors.append("Linked collection or placement marker is missing")
    objects = []
    linked_path = None
    actual_bounds = None
    direct_links = -1
else:
    linked_path = Path(bpy.path.abspath(collection.library.filepath)).resolve() if collection.library else None
    if linked_path != asset_path:
        errors.append(f"Linked library path mismatch: {linked_path}")
    if marker.instance_collection != collection or marker.instance_type != "COLLECTION":
        errors.append("Marker does not instance the expected collection")
    origin = record.get("placement_origin_xy_m")
    if not origin or max(abs(float(marker.location[i]) - float(origin[i])) for i in range(2)) > 0.001:
        errors.append("Marker placement does not match manifest origin")
    direct_links = sum(child == collection for child in scene.collection.children)
    if direct_links:
        errors.append(f"Source collection remains directly linked {direct_links} time(s)")
    objects = list(collection.all_objects)
    if len(objects) != record.get("object_count"):
        errors.append(f"Object count mismatch: {len(objects)} != {record.get('object_count')}")
    cache = {}

    def local_matrix(obj):
        if obj in cache:
            return cache[obj]
        matrix = obj.matrix_local.copy()
        if obj.parent is not None:
            matrix = local_matrix(obj.parent) @ matrix
        cache[obj] = matrix
        return matrix

    points = [local_matrix(obj) @ Vector(corner)
              for obj in objects if obj.type == "MESH" for corner in obj.bound_box]
    points = [Vector((p.x + marker.location.x, p.y + marker.location.y, p.z)) for p in points]
    actual_bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)] if points else None
expected_bounds = record.get("bounds_world_m")
max_bounds_error = max(abs(actual_bounds[i][j] - expected_bounds[i][j])
                       for i in range(3) for j in range(2)) if actual_bounds and expected_bounds else None
if max_bounds_error is None or max_bounds_error > 0.01:
    errors.append(f"World-bounds error exceeds 1 cm: {max_bounds_error}")

report = {
    "status": "PASS" if not errors else "FAIL",
    "master_file": str(Path(bpy.data.filepath).resolve()),
    "fresh_open_blender_version": bpy.app.version_string,
    "scene": scene.name,
    "scene_object_count": len(scene.objects),
    "checked_building": ASSET_ID,
    "score": record.get("independent_grade_score"),
    "sha256": actual_sha,
    "linked_path": str(linked_path) if linked_path else None,
    "placement_xy_m": [float(marker.location.x), float(marker.location.y)] if marker else None,
    "object_count": len(objects),
    "mesh_object_count": sum(obj.type == "MESH" for obj in objects),
    "direct_collection_links": direct_links,
    "actual_bounds_world_m": actual_bounds,
    "expected_bounds_world_m": expected_bounds,
    "max_world_bounds_error_m": max_bounds_error,
    "errors": errors,
}
out = ROOT / "audit" / "master_integration_alpha_omicron_pi_2026-10-27.json"
out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
if errors:
    raise RuntimeError("AOII master verification failed")
