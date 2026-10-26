import bpy
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
asset = root / "modular/buildings/south_hall.blend"
report_path = root / "audit/south_hall_refine/exterior_bounds_r2.json"
origin_xy = [-1091.6500244140625, -131.2249984741211]
collection = bpy.data.collections.get("12_South_Hall_Exterior")
if collection is None:
    raise RuntimeError("Exterior collection is missing")
depsgraph = bpy.context.evaluated_depsgraph_get()
points = []
mesh_count = 0
for obj in collection.all_objects:
    if obj.type != "MESH":
        continue
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        points.extend(evaluated.matrix_world @ vertex.co for vertex in mesh.vertices)
        mesh_count += 1
    finally:
        evaluated.to_mesh_clear()
if not points:
    raise RuntimeError("Exterior collection has no evaluated mesh vertices")
local_bounds = [[min(point[axis] for point in points), max(point[axis] for point in points)] for axis in range(3)]
world_bounds = [
    [local_bounds[axis][0] + origin_xy[axis], local_bounds[axis][1] + origin_xy[axis]] if axis < 2
    else local_bounds[axis]
    for axis in range(3)
]
report = {
    "asset": str(asset),
    "asset_sha256": hashlib.sha256(asset.read_bytes()).hexdigest(),
    "evaluated_collection": collection.name,
    "mesh_object_count": mesh_count,
    "local_bounds_axis_major_m": local_bounds,
    "manifest_placement_origin_xy_m": origin_xy,
    "world_bounds_axis_major_m": world_bounds,
    "method": "Fresh standalone Blender 5.2.3 reopen; evaluated mesh vertices of the exterior collection only; local XY translated by the manifest placement origin.",
}
report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
