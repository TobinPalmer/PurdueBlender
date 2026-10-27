"""Independent read-only inspection of the frozen Windsor R4 library."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
COLLECTION_NAME = "Asset_massing_windsor_halls_80aeb51"
collection = bpy.data.collections.get(COLLECTION_NAME)
if collection is None:
    raise RuntimeError(f"Missing {COLLECTION_NAME}")
meshes = [obj for obj in collection.all_objects if obj.type == "MESH"]
shells = {}
for fid in (63, 64, 65, 66):
    marker = f"FID {fid}) | structural footprint shell"
    obj = next((obj for obj in meshes if marker in obj.name), None)
    if obj is None:
        raise RuntimeError(f"Missing structural shell {fid}")
    # Extract vertices from the largest near-planar polygon at the bottom face.
    # This directly interrogates the reopened library rather than trusting its report.
    faces = []
    for face in obj.data.polygons:
        points = [obj.matrix_world @ obj.data.vertices[i].co for i in face.vertices]
        z_span = max(p.z for p in points) - min(p.z for p in points)
        if z_span < 1e-5:
            faces.append((face.area, points))
    if not faces:
        raise RuntimeError(f"Could not find a planar shell loop for FID {fid}")
    _, points = max(faces, key=lambda row: row[0])
    shells[str(fid)] = [[round(p.x, 8), round(p.y, 8)] for p in points]

points = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
linked = [lib.filepath for lib in bpy.data.libraries if lib.filepath]
external_images = [image.filepath for image in bpy.data.images
                   if image.source == "FILE" and image.filepath and not image.packed_file]
used_materials = sorted({mat.name for obj in meshes for mat in obj.data.materials if mat})
result = {
    "fresh_open": True,
    "blender_version": bpy.app.version_string,
    "scene": bpy.context.scene.name,
    "collection": collection.name,
    "object_count": len(collection.all_objects),
    "mesh_count": len(meshes),
    "mesh_vertices": sum(len(obj.data.vertices) for obj in meshes),
    "mesh_faces": sum(len(obj.data.polygons) for obj in meshes),
    "materials": used_materials,
    "linked_libraries": linked,
    "unpacked_external_images": external_images,
    "bounds_local": {
        "x": [min(p.x for p in points), max(p.x for p in points)],
        "y": [min(p.y for p in points), max(p.y for p in points)],
        "z": [min(p.z for p in points), max(p.z for p in points)],
    },
    "structural_shell_xy": shells,
}
(HERE / "fresh_open_probe.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print("INDEPENDENT_WINDSOR_PROBE", HERE / "fresh_open_probe.json")
