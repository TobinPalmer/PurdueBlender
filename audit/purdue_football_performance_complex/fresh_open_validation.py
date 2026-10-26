import bpy
import hashlib
import json
import os
from mathutils import Vector

asset_id = "massing_purdue_football_performance_complex_f106c29"
blend_path = bpy.data.filepath
collection_name = "Asset_" + asset_id
collection = bpy.data.collections.get(collection_name)
objects = list(collection.all_objects) if collection else []
mesh_curve = [obj for obj in objects if obj.type in {"MESH", "CURVE", "FONT", "SURFACE", "META"}]
coords = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
bounds = None
if coords:
    bounds = {
        "min": [min(v[i] for v in coords) for i in range(3)],
        "max": [max(v[i] for v in coords) for i in range(3)],
    }
images = []
for image in bpy.data.images:
    if image.source == "FILE" and image.filepath and not image.packed_file:
        images.append(bpy.path.abspath(image.filepath))
sha = hashlib.sha256(open(blend_path, "rb").read()).hexdigest()
result = {
    "blend_path": os.path.abspath(blend_path),
    "sha256": sha,
    "scene": bpy.context.scene.name,
    "collection_found": collection is not None,
    "collection": collection_name,
    "asset_object_count": len(objects),
    "geometry_object_count": len(mesh_curve),
    "material_count": len({m.name for o in objects for m in o.data.materials if m}),
    "bounds_world_m": bounds,
    "unpacked_external_image_paths": images,
}
out_path = os.path.join(os.path.dirname(blend_path), "..", "..", "audit", "purdue_football_performance_complex", "fresh_open_validation.json")
out_path = os.path.abspath(out_path)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)
print("FRESH_OPEN_VALIDATION=" + json.dumps(result))
