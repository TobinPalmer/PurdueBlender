import json
import os
import bpy
from mathutils import Vector

asset_id = "massing_slayter_center_for_performing_arts_f45259b"
collection_name = "Asset_" + asset_id
collection = bpy.data.collections.get(collection_name)
assert collection is not None, f"Missing exported collection {collection_name}"
objects = list(collection.objects)
assert len(objects) == 1, f"Expected one exported object, found {len(objects)}"
obj = objects[0]
assert obj.type == "MESH", f"Expected one mesh object, found {obj.type}"
assert all(abs(v) < 1e-6 for v in (*obj.location, *obj.rotation_euler)), "Object location/rotation must be identity"
assert all(abs(v - 1.0) < 1e-6 for v in obj.scale), "Object scale must be identity"
bpy.context.view_layer.update()
world_bounds = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
bounds = {
    axis: [round(min(p[i] for p in world_bounds), 6), round(max(p[i] for p in world_bounds), 6)]
    for i, axis in enumerate("xyz")
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
    "modifiers": [f"{modifier.name}:{modifier.type}" for modifier in obj.modifiers],
    "identity_object_transform": True,
    "bounds_m": bounds,
    "external_unpacked_images": external_images,
    "passed": bool(obj.data.vertices and obj.data.polygons and not external_images),
}
output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "slayter_reopen_validation.json")
with open(output, "w", encoding="utf-8") as handle:
    json.dump(result, handle, indent=2)
print("REOPEN_VALIDATION_JSON=" + json.dumps(result, sort_keys=True))
assert result["passed"], "Saved asset validation failed"
