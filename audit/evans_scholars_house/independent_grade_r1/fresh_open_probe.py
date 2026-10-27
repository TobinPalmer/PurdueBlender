"""Independent reopen and portability probe for Evans Scholars House."""
import hashlib
import json
from pathlib import Path
import bpy
from mathutils import Vector

asset = Path(bpy.data.filepath).resolve()
collection = bpy.data.collections.get("Asset_massing_house_301841610_b6ad6ed")
if collection is None:
    raise RuntimeError("Expected Evans Scholars asset collection is absent")
objects = list(collection.all_objects)
images = []
for image in bpy.data.images:
    if image.source == "FILE":
        path = bpy.path.abspath(image.filepath)
        if not Path(path).is_file() and not image.packed_file:
            images.append({"path": path, "missing": True, "packed": False})
        elif not image.packed_file and image.filepath:
            images.append({"path": path, "missing": False, "packed": False})
linked_libraries = [str(lib.filepath) for lib in bpy.data.libraries if lib.filepath]
mesh_objects = [obj for obj in objects if obj.type == "MESH"]
points = [obj.matrix_world @ Vector(corner) for obj in mesh_objects for corner in obj.bound_box]
result = {
    "asset": str(asset),
    "sha256": hashlib.sha256(asset.read_bytes()).hexdigest(),
    "blender": bpy.app.version_string,
    "scene": bpy.context.scene.name,
    "collection": collection.name,
    "object_count": len(objects),
    "mesh_count": len(mesh_objects),
    "material_count": len({mat.name for obj in mesh_objects for mat in obj.data.materials if mat}),
    "linked_libraries": linked_libraries,
    "external_images": images,
    "bounds_local_m": [[min(point[axis] for point in points), max(point[axis] for point in points)]
                        for axis in range(3)],
}
out = asset.parents[2] / "audit" / "evans_scholars_house" / "independent_grade_r1" / "fresh_open_probe.json"
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
if result["linked_libraries"] or any(item.get("missing") for item in images):
    raise RuntimeError("Portability probe found linked dependencies or missing image files")
