import json
import math
import os
import bpy
from mathutils import Vector

asset_id = "massing_house_301841608_d56a4c4"
audit_dir = os.path.dirname(os.path.abspath(__file__))
collection = bpy.data.collections.get("Asset_" + asset_id)
assert collection is not None and len(collection.objects) == 1, "Expected one object in assigned collection"
obj = collection.objects[0]
assert obj.type == "MESH", f"Expected mesh, found {obj.type}"
assert all(abs(value) < 1e-6 for value in (*obj.location, *obj.rotation_euler)), "Object location/rotation must be identity"
assert all(abs(value-1.0) < 1e-6 for value in obj.scale), "Object scale must be identity"

with open(os.path.join(audit_dir, "source_feature_757_raw.json"), encoding="utf-8-sig") as handle:
    feature = json.load(handle)
assert feature["attributes"]["FID"] == 757
ring = feature["geometry"]["rings"][0]
if ring[0] == ring[-1]:
    ring = ring[:-1]
lat0, lon0 = 40.4274, -86.9137
expected = [
    Vector(((lon-lon0)*111412.84*math.cos(math.radians(lat0)), (lat-lat0)*111040.0, 0.0))
    for lon,lat in ring
]
base_vertices = [vertex.co.copy() for vertex in obj.data.vertices if abs(vertex.co.z) < 1e-5]
errors = [min((candidate-point).length for candidate in base_vertices) for point in expected]
max_error = max(errors)
assert max_error < 1e-4, f"GIS footprint base residual is {max_error:.6f} m"

bpy.context.view_layer.update()
world = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
bounds = {
    axis: [round(min(point[index] for point in world),6), round(max(point[index] for point in world),6)]
    for index,axis in enumerate("xyz")
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
    "collection_object_count": len(collection.objects),
    "object_name": obj.name,
    "object_type": obj.type,
    "identity_object_transform": True,
    "source_fid": feature["attributes"]["FID"],
    "source_ring_vertices": len(expected),
    "matched_source_ring_vertices": len(expected),
    "max_source_ring_error_m": round(max_error, 9),
    "mesh_vertices": len(obj.data.vertices),
    "mesh_edges": len(obj.data.edges),
    "mesh_faces": len(obj.data.polygons),
    "bounds_world_m": bounds,
    "modifiers": [f"{modifier.name}:{modifier.type}" for modifier in obj.modifiers],
    "external_unpacked_images": external_images,
    "passed": bool(obj.data.vertices and obj.data.polygons and not external_images),
}
with open(os.path.join(audit_dir, "reopen_validation.json"), "w", encoding="utf-8") as handle:
    json.dump(result, handle, indent=2)
    handle.write("\n")
print("REOPEN_VALIDATION_JSON="+json.dumps(result, sort_keys=True))
assert result["passed"], "Asset validation failed"
