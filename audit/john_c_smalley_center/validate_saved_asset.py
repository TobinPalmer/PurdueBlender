import json
import math
import os
import bpy
from mathutils import Vector

asset_id = "massing_smalley_center_1902608"
collection_name = "Asset_" + asset_id
audit_dir = os.path.dirname(os.path.abspath(__file__))
collection = bpy.data.collections.get(collection_name)
assert collection is not None, f"Missing exported collection {collection_name}"
objects = list(collection.objects)
assert len(objects) == 1, f"Expected one exported object, found {len(objects)}"
obj = objects[0]
assert obj.type == "MESH", f"Expected a mesh object, found {obj.type}"
assert all(abs(value) < 1e-6 for value in (*obj.location, *obj.rotation_euler)), "Object location/rotation must be identity"
assert all(abs(value - 1.0) < 1e-6 for value in obj.scale), "Object scale must be identity"

with open(os.path.join(audit_dir, "source_feature_225_raw.json"), encoding="utf-8-sig") as handle:
    feature = json.load(handle)
ring = feature["geometry"]["rings"][0]
if ring[0] == ring[-1]:
    ring = ring[:-1]
origin_lat, origin_lon = 40.4274, -86.9137
expected = [
    Vector(((lon - origin_lon) * 111412.84 * math.cos(math.radians(origin_lat)),
            (lat - origin_lat) * 111040.0, 0.0))
    for lon, lat in ring
]
actual_bottom = [vertex.co.copy() for vertex in obj.data.vertices if abs(vertex.co.z) < 1e-5]
nearest_errors = [min((candidate - point).length for candidate in actual_bottom) for point in expected]
max_footprint_error = max(nearest_errors)
assert max_footprint_error < 1e-4, f"Footprint vertices differ from transformed GIS ring by {max_footprint_error:.6f} m"

bpy.context.view_layer.update()
world_bounds = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
bounds = {
    axis: [round(min(point[index] for point in world_bounds), 6), round(max(point[index] for point in world_bounds), 6)]
    for index, axis in enumerate("xyz")
}
external_images = [
    image.filepath for image in bpy.data.images
    if image.source == "FILE" and image.filepath and not image.packed_file
]
result = {
    "asset_id": asset_id,
    "blend_file": bpy.data.filepath,
    "reopened_in_background_blender": True,
    "collection": collection.name,
    "collection_object_count": len(objects),
    "object_name": obj.name,
    "object_type": obj.type,
    "vertices": len(obj.data.vertices),
    "edges": len(obj.data.edges),
    "faces": len(obj.data.polygons),
    "identity_object_transform": True,
    "official_source_fid": feature["attributes"]["FID"],
    "official_ring_vertices": len(expected),
    "matched_source_ring_vertices": len(expected),
    "max_footprint_vertex_error_m": round(max_footprint_error, 9),
    "bounds_m": bounds,
    "modifiers": [f"{modifier.name}:{modifier.type}" for modifier in obj.modifiers],
    "external_unpacked_images": external_images,
    "passed": bool(obj.data.vertices and obj.data.polygons and not external_images),
}
output = os.path.join(audit_dir, "reopen_validation.json")
with open(output, "w", encoding="utf-8") as handle:
    json.dump(result, handle, indent=2)
print("REOPEN_VALIDATION_JSON=" + json.dumps(result, sort_keys=True))
assert result["passed"], "Saved asset validation failed"
