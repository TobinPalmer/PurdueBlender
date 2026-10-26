"""Independent fresh-process check of the frozen University Hall R6 asset."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/university_hall.blend"
EXPECTED_SHA256 = "5fb431e4a8c6d5f47e50fc7085de981f64a2f4982b73af57830cdac162bd9da2"
OUTPUT = ROOT / "audit/university_hall_refine/independent_grade_r6_reopen.json"

actual_sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
if actual_sha != EXPECTED_SHA256:
    raise RuntimeError(f"R6 hash mismatch: {actual_sha}")
if Path(bpy.data.filepath).resolve() != ASSET.resolve():
    raise RuntimeError("Start Blender with the saved University Hall asset already open")
collection = bpy.data.collections.get("Asset_university_hall")
scene = bpy.context.scene
root = bpy.data.objects.get("AssetRoot_university_hall")
if collection is None or root is None:
    raise RuntimeError("Expected University Hall export collection or root is missing")
objects = list(collection.all_objects)
meshes = [obj for obj in objects if obj.type == "MESH"]
used_materials = {mat.name: mat for obj in meshes for mat in obj.data.materials if mat}
materialless = [obj.name for obj in meshes if not obj.data.materials or all(mat is None for mat in obj.data.materials)]
invalid_slots = []
for obj in meshes:
    for poly in obj.data.polygons:
        if poly.material_index >= len(obj.data.materials) or obj.data.materials[poly.material_index] is None:
            invalid_slots.append(obj.name)
            break
missing_images = []
image_nodes = []
for mat in used_materials.values():
    if not mat.use_nodes:
        continue
    for node in mat.node_tree.nodes:
        if node.type != "TEX_IMAGE" or node.image is None:
            continue
        path = bpy.path.abspath(node.image.filepath) if node.image.source == "FILE" else None
        exists = bool(path and Path(path).exists()) if node.image.source == "FILE" else True
        if node.image.source == "FILE" and path and not exists and not node.image.packed_file:
            missing_images.append(path)
        image_nodes.append({"material": mat.name, "image": node.image.name, "source": node.image.source,
                            "filepath": path, "exists": exists, "packed": bool(node.image.packed_file)})
linked_libraries = [{"name": lib.name, "filepath": bpy.path.abspath(lib.filepath)} for lib in bpy.data.libraries]
depsgraph = bpy.context.evaluated_depsgraph_get()
points = []
for obj in meshes:
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        points.extend(evaluated.matrix_world @ vert.co for vert in mesh.vertices)
    finally:
        evaluated.to_mesh_clear()
bounds = [[min(point[i] for point in points), max(point[i] for point in points)] for i in range(3)] if points else None

def identity(obj):
    return {
        "name": obj.name,
        "location": list(obj.location),
        "rotation_euler": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "matrix_world": [[float(obj.matrix_world[r][c]) for c in range(4)] for r in range(4)],
    }

def named_objects(patterns):
    return [obj.name for obj in objects if any(pattern.casefold() in obj.name.casefold() for pattern in patterns)]

report = {
    "validation": "Independent fresh-process reopen of the exact saved R6 asset",
    "asset": str(ASSET),
    "sha256": actual_sha,
    "blender_version": bpy.app.version_string,
    "scene": scene.name,
    "collection": collection.name,
    "collection_object_count": len(objects),
    "mesh_count": len(meshes),
    "object_type_counts": {kind: sum(obj.type == kind for obj in objects) for kind in sorted({obj.type for obj in objects})},
    "root": identity(root),
    "evaluated_bounds_local_m_axis_major": bounds,
    "used_material_count": len(used_materials),
    "used_material_names": sorted(used_materials),
    "materialless_meshes": materialless,
    "invalid_material_indices": sorted(set(invalid_slots)),
    "image_nodes": image_nodes,
    "missing_external_images": sorted(set(missing_images)),
    "linked_libraries": linked_libraries,
    "named_gallery_stair_landing_objects": {
        "gallery": named_objects(["gallery", "ring", "void"]),
        "stair": named_objects(["stair", "flight"]),
        "landing": named_objects(["landing"]),
        "reclaimed_display_columns": named_objects(["reclaimed", "recovered", "display column"]),
    },
}
OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
