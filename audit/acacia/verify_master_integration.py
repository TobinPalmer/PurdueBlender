"""Fresh-open structural verification for Acacia's master integration."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
MODULAR = ROOT / "modular"
ASSET_ID = "massing_house_301841251_8a9a05b"
manifest = json.loads((MODULAR / "manifest.json").read_text(encoding="utf-8"))
record = next(a for a in manifest["assets"] if a["id"] == ASSET_ID)
scene = bpy.context.scene
marker_name = f"Placement_{ASSET_ID}"
marker = bpy.data.objects.get(marker_name)
assert marker is not None and marker.instance_collection is not None
collection = marker.instance_collection
assert marker.instance_type == "COLLECTION"
assert collection.name == record["collection"]
linked_path = Path(bpy.path.abspath(collection.library.filepath)).resolve()
expected_path = (MODULAR / record["file"]).resolve()
assert linked_path == expected_path
assert collection not in list(scene.collection.children), "duplicate direct collection link"
assert record["kind"] == "detailed" and record.get("local_coordinates") is True

members = set(collection.all_objects)
cache = {}

def local_matrix(obj):
    if obj in cache:
        return cache[obj]
    matrix = obj.matrix_local.copy()
    if obj.parent in members:
        matrix = local_matrix(obj.parent) @ matrix
    cache[obj] = matrix
    return matrix

points = []
for obj in collection.all_objects:
    if obj.type not in {"MESH", "CURVE", "FONT", "SURFACE", "META"}:
        continue
    matrix = marker.matrix_world @ local_matrix(obj)
    points.extend(matrix @ Vector(corner) for corner in obj.bound_box)
assert points, "linked asset has no bounded geometry"
world_bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]
reference_bounds = record["source_bounds_world_m"]
max_bounds_delta = max(abs(world_bounds[i][j] - reference_bounds[i][j])
                       for i in range(3) for j in range(2))
placement_expected = record["placement_origin_xy_m"]
placement_delta = max(abs(float(marker.location[i]) - placement_expected[i]) for i in range(2))
marker_counts = sum(1 for obj in scene.objects if obj.name == marker_name)

report = {
    "status": "PASS" if marker_counts == 1 and max_bounds_delta <= 0.001 and placement_delta <= 0.001 else "FAIL",
    "master_path": str(ROOT / "purdue_campus_master.blend"),
    "asset_id": ASSET_ID,
    "asset_path": str(expected_path),
    "manifest_kind": record["kind"],
    "fresh_open": True,
    "marker": marker_name,
    "marker_count": marker_counts,
    "marker_location_xy_m": [float(marker.location[0]), float(marker.location[1])],
    "manifest_placement_xy_m": placement_expected,
    "placement_delta_m": placement_delta,
    "instance_collection": collection.name,
    "instance_object_count": len(collection.all_objects),
    "direct_scene_root_link": collection in list(scene.collection.children),
    "linked_library_path": str(linked_path),
    "world_bounds_m": world_bounds,
    "source_bounds_before_localization_m": reference_bounds,
    "max_world_bounds_delta_m": max_bounds_delta,
}
out = ROOT / "audit" / "acacia" / "master_integration_2026-10-26.json"
out.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
if report["status"] != "PASS":
    raise RuntimeError("Acacia fresh-open integration verification failed")
