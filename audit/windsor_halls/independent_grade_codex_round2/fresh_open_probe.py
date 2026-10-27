import bpy
import hashlib
import json
from pathlib import Path

asset = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_windsor_halls_80aeb51.blend")
expected_sha = "38f4aad7181339a573c2eeb5b6151d116d68bb9c60bb92c040b09516ae676135"
actual_sha = hashlib.sha256(asset.read_bytes()).hexdigest()
collection_name = "Asset_massing_windsor_halls_80aeb51"
scene_name = "Building_massing_windsor_halls_80aeb51"
collection = bpy.data.collections.get(collection_name)
scene = bpy.data.scenes.get(scene_name)
errors = []
if actual_sha != expected_sha:
    errors.append(f"SHA mismatch: {actual_sha}")
if collection is None:
    errors.append(f"missing collection {collection_name}")
if scene is None:
    errors.append(f"missing scene {scene_name}")

objects = list(collection.all_objects) if collection else []
meshes = [obj for obj in objects if obj.type == "MESH"]
used_materials = {slot.material.name for obj in objects for slot in obj.material_slots if slot.material}
materialless_meshes = [obj.name for obj in meshes if not any(slot.material for slot in obj.material_slots)]
missing_images = []
for image in bpy.data.images:
    if image.source == "FILE" and image.packed_file is None and image.filepath:
        resolved = Path(bpy.path.abspath(image.filepath))
        if not resolved.exists():
            missing_images.append(str(resolved))
linked_libraries = [lib.filepath for lib in bpy.data.libraries]
if materialless_meshes:
    errors.append(f"meshes without materials: {len(materialless_meshes)}")
if missing_images:
    errors.append(f"missing image dependencies: {len(missing_images)}")
if linked_libraries:
    errors.append(f"unexpected linked-library dependencies: {len(linked_libraries)}")

bounds = None
if meshes:
    points = [obj.matrix_world @ __import__("mathutils").Vector(corner)
              for obj in meshes for corner in obj.bound_box]
    bounds = {axis: [min(float(p[i]) for p in points), max(float(p[i]) for p in points)]
              for i, axis in enumerate(("x", "y", "z"))}

result = {
    "review_type": "independent fresh-open",
    "blender_version": bpy.app.version_string,
    "asset": str(asset),
    "asset_sha256": actual_sha,
    "expected_sha256": expected_sha,
    "sha_match": actual_sha == expected_sha,
    "fresh_open": True,
    "scene": scene.name if scene else None,
    "collection": collection.name if collection else None,
    "collection_object_count": len(objects),
    "mesh_count": len(meshes),
    "vertex_count": sum(len(obj.data.vertices) for obj in meshes),
    "face_count": sum(len(obj.data.polygons) for obj in meshes),
    "used_material_count": len(used_materials),
    "used_materials": sorted(used_materials),
    "materialless_mesh_count": len(materialless_meshes),
    "missing_external_images": missing_images,
    "linked_libraries": linked_libraries,
    "mesh_bounds_m": bounds,
    "errors": errors,
}
output = Path(__file__).resolve().parent / "fresh_open_probe.json"
output.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result))
if errors:
    raise RuntimeError("Windsor independent fresh-open failed")
