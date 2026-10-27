import bpy
import hashlib
import json
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
manifest_path = repo / "modular" / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
asset_id = "massing_house_860826641_2c90f97"
record = next(item for item in manifest["assets"] if item["id"] == asset_id)
asset_path = (repo / "modular" / record["file"]).resolve()
marker = bpy.data.objects.get(f"Placement_{asset_id}")
root = bpy.context.scene.collection
errors = []

if marker is None:
    errors.append("placement marker missing")
if marker is not None:
    if marker.instance_type != "COLLECTION":
        errors.append(f"wrong instance type: {marker.instance_type}")
    linked = marker.instance_collection
    if linked is None:
        errors.append("instance collection missing")
    else:
        if linked.name != record["collection"]:
            errors.append(f"wrong collection: {linked.name}")
        if linked.library is None:
            errors.append("source collection is not linked from a library")
        else:
            actual_path = Path(bpy.path.abspath(linked.library.filepath)).resolve()
            if actual_path != asset_path:
                errors.append(f"wrong linked path: {actual_path}")
        expected_xy = record["placement_origin_xy_m"]
        actual_xy = [float(marker.location.x), float(marker.location.y)]
        if max(abs(actual_xy[i] - expected_xy[i]) for i in range(2)) > 0.001:
            errors.append(f"marker XY mismatch: {actual_xy} vs {expected_xy}")
        if linked in list(root.children):
            errors.append("detailed source collection is also directly linked at campus root")

fresh_sha = hashlib.sha256(asset_path.read_bytes()).hexdigest()
expected_sha = "1f1b3efa2fd0d3dd756ccbd6556ee5a4f8fce0539eae0f5088e1190c8992c976"
if fresh_sha != expected_sha:
    errors.append(f"asset SHA changed: {fresh_sha}")

local = record["local_bounds_m"]
origin = record["placement_origin_xy_m"]
expected_world = [
    [local[0][0] + origin[0], local[0][1] + origin[0]],
    [local[1][0] + origin[1], local[1][1] + origin[1]],
    list(local[2]),
]
record_world = record["bounds_world_m"]
bounds_error = max(abs(expected_world[i][j] - record_world[i][j])
                   for i in range(3) for j in range(2))
if bounds_error > 0.001:
    errors.append(f"manifest world bounds don't match local bounds plus marker: {bounds_error} m")

result = {
    "status": "PASS" if not errors else "FAIL",
    "asset_id": asset_id,
    "fresh_open_scene": bpy.context.scene.name,
    "source_asset": str(asset_path),
    "asset_sha256": fresh_sha,
    "collection": marker.instance_collection.name if marker and marker.instance_collection else None,
    "placement_xy_m": list(marker.location[:2]) if marker else None,
    "manifest_placement_xy_m": origin,
    "linked_collection_object_count": len(marker.instance_collection.all_objects) if marker and marker.instance_collection else None,
    "linked_collection_library": marker.instance_collection.library.filepath if marker and marker.instance_collection and marker.instance_collection.library else None,
    "world_bounds_error_m": bounds_error,
    "errors": errors,
}
out = repo / "audit" / "delta_sigma_phi" / "master_integration_2026-10-26.json"
out.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result))
if errors:
    raise RuntimeError("Delta Sigma Phi master integration validation failed")
