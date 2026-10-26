import bpy
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
asset = root / "modular/buildings/ray_w_herrick_laboratories.blend"
report_path = root / "audit/ray_w_herrick_refine/exterior_bounds_r2.json"
origin_xy = [-531.9590659304099, -569.0631943790936]
asset_collection = bpy.data.collections.get("Asset_ray_w_herrick_laboratories")
if asset_collection is None:
    raise RuntimeError("HLAB asset collection is missing")
exterior_names = {"Structure", "Facade_Details"}
exterior_collections = [bpy.data.collections[name] for name in exterior_names]
objects = set(obj for obj in asset_collection.objects if obj.type == "MESH")
for collection in exterior_collections:
    objects.update(obj for obj in collection.all_objects if obj.type == "MESH")
depsgraph = bpy.context.evaluated_depsgraph_get()
points = []
for obj in objects:
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        points.extend(evaluated.matrix_world @ vertex.co for vertex in mesh.vertices)
    finally:
        evaluated.to_mesh_clear()
if not points:
    raise RuntimeError("No evaluated exterior mesh vertices")
local_bounds = [[min(point[axis] for point in points), max(point[axis] for point in points)] for axis in range(3)]
world_bounds = [
    [local_bounds[axis][0] + origin_xy[axis], local_bounds[axis][1] + origin_xy[axis]] if axis < 2
    else local_bounds[axis]
    for axis in range(3)
]
report = {
    "asset": str(asset),
    "asset_sha256": hashlib.sha256(asset.read_bytes()).hexdigest(),
    "asset_collection": asset_collection.name,
    "exterior_collections": sorted(exterior_names),
    "evaluated_mesh_object_count": len(objects),
    "local_bounds_axis_major_m": local_bounds,
    "manifest_placement_origin_xy_m": origin_xy,
    "world_bounds_axis_major_m": world_bounds,
    "method": "Fresh standalone Blender 5.2.3 reopen; evaluated mesh vertices in Structure and Facade_Details plus direct mesh objects in the asset collection; preview stage and schematic interior excluded.",
}
report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
