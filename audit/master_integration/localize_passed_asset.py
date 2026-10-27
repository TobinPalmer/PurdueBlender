"""Move an approved campus-coordinate building library into local coordinates.

Run with Blender on an individual building file:
  blender -b asset.blend --python localize_passed_asset.py -- BUILDING_ID X Y AUDIT_JSON

The master placement marker later translates the local library by (X, Y, 0).
The script preserves every evaluated world-space matrix and verifies the
round-trip bounds before saving.
"""
import bpy
import hashlib
import json
import sys
from pathlib import Path
from mathutils import Matrix, Vector


args = sys.argv[sys.argv.index("--") + 1:]
if len(args) != 4:
    raise SystemExit("Expected BUILDING_ID ORIGIN_X ORIGIN_Y AUDIT_JSON")
building_id = args[0]
origin = Vector((float(args[1]), float(args[2]), 0.0))
report_path = Path(args[3]).resolve()
asset_path = Path(bpy.data.filepath).resolve()
collection_name = f"Asset_{building_id}"
scene_name = f"Building_{building_id}"
collection = bpy.data.collections.get(collection_name)
scene = bpy.data.scenes.get(scene_name)
if collection is None or scene is None:
    raise RuntimeError(f"Missing expected collection/scene for {building_id}")
if collection.get("local_coordinates"):
    raise RuntimeError(f"{building_id} is already localized; refusing a second translation")


def bounds(objects):
    points = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        if obj.type not in {"MESH", "CURVE", "FONT"}:
            continue
        evaluated = obj.evaluated_get(depsgraph)
        for corner in evaluated.bound_box:
            points.append(evaluated.matrix_world @ Vector(corner))
    if not points:
        raise RuntimeError("No evaluated geometry in the approved collection")
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]


objects = list(collection.all_objects)
old_bounds = bounds(objects)
if any(obj.library is not None for obj in objects):
    raise RuntimeError("Candidate contains linked objects; localize a clean standalone asset")
root_name = f"AssetRoot_{building_id}"
if bpy.data.objects.get(root_name) is not None:
    raise RuntimeError(f"{root_name} already exists; inspect asset before proceeding")

# All geometry gets a single local root. Preserve each original world matrix,
# subtracting only the master placement origin from XY.
root = bpy.data.objects.new(root_name, None)
root.empty_display_type = "PLAIN_AXES"
root.empty_display_size = 2.0
collection.objects.link(root)
root.matrix_world = Matrix.Identity(4)
for obj in objects:
    world = obj.matrix_world.copy()
    world.translation -= origin
    obj.parent = root
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.matrix_world = world

# Keep any non-asset camera or light in this standalone scene framing the now
# local asset; they remain outside the linked master collection.
asset_object_set = set(objects) | {root}
for obj in scene.objects:
    if obj not in asset_object_set and obj.type in {"CAMERA", "LIGHT"}:
        world = obj.matrix_world.copy()
        world.translation -= origin
        obj.matrix_world = world

collection["local_coordinates"] = True
collection["placement_origin_xy_m"] = [float(origin.x), float(origin.y)]
collection["building_id"] = building_id
root["building_id"] = building_id
scene["building_id"] = building_id
scene["placement_origin_xy_m"] = [float(origin.x), float(origin.y)]
bpy.context.view_layer.update()
local_bounds = bounds(objects)
reconstructed_bounds = [
    [local_bounds[i][j] + (origin[i] if i < 2 else 0.0) for j in range(2)]
    for i in range(3)
]
max_world_error = max(
    abs(reconstructed_bounds[i][j] - old_bounds[i][j])
    for i in range(3) for j in range(2)
)
if max_world_error > 0.01:
    raise RuntimeError(f"Localization changed campus bounds by {max_world_error:.6f} m")
if not all(obj.parent == root for obj in objects):
    raise RuntimeError("Not all building objects were parented to the local asset root")

bpy.ops.wm.save_as_mainfile(filepath=str(asset_path))
digest = hashlib.sha256(asset_path.read_bytes()).hexdigest()
report = {
    "status": "PASS",
    "building_id": building_id,
    "asset_path": str(asset_path),
    "asset_sha256": digest,
    "scene": scene.name,
    "collection": collection.name,
    "object_count_including_root": len(collection.all_objects),
    "geometry_object_count": len(objects),
    "placement_origin_xy_m": [float(origin.x), float(origin.y)],
    "original_bounds_world_m": old_bounds,
    "local_bounds_m": local_bounds,
    "reconstructed_bounds_world_m": reconstructed_bounds,
    "max_world_bounds_error_m": max_world_error,
    "all_geometry_parented_to_root": True,
    "validation": "Geometry was translated into the local frame; master placement marker restores original campus XYZ bounds.",
}
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report))
