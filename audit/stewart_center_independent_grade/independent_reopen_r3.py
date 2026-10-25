import bpy
import collections
import hashlib
import json
from pathlib import Path
from mathutils import Vector

asset_path = Path(bpy.data.filepath)
collection = bpy.data.collections.get("Asset_stewart_center")
objects = list(collection.all_objects) if collection else []
meshes = [obj for obj in objects if obj.type == "MESH"]
materialless = [obj.name for obj in meshes if not obj.data.materials or all(mat is None for mat in obj.data.materials)]
missing_images = []
for image in bpy.data.images:
    if image.source == "FILE" and image.filepath:
        resolved = Path(bpy.path.abspath(image.filepath))
        if not resolved.exists():
            missing_images.append({"image": image.name, "path": image.filepath})

points = []
for obj in objects:
    if obj.type in {"MESH", "CURVE", "FONT"}:
        points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
bounds = [[min(point[i] for point in points), max(point[i] for point in points)] for i in range(3)] if points else None
root = bpy.data.objects.get("AssetRoot_stewart_center")
report = {
    "asset": str(asset_path),
    "sha256": hashlib.sha256(asset_path.read_bytes()).hexdigest(),
    "blender_version": bpy.app.version_string,
    "collection_exists": collection is not None,
    "collection": collection.name if collection else None,
    "object_count": len(objects),
    "type_counts": dict(collections.Counter(obj.type for obj in objects)),
    "mesh_count": len(meshes),
    "material_count": len({mat.name for obj in meshes for mat in obj.data.materials if mat}),
    "materialless_meshes": materialless,
    "missing_external_images": missing_images,
    "root_matrix_world": [[float(value) for value in row] for row in root.matrix_world] if root else None,
    "bounds_world_m": bounds,
    "cameras_in_asset_collection": [obj.name for obj in objects if obj.type == "CAMERA"],
}
output = Path(__file__).with_name("independent_reopen_r3.json")
output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
