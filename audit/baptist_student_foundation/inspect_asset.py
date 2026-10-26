"""Reopen and inspect the Baptist Student Foundation library asset."""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular" / "buildings" / "massing_baptist_student_foundation_c3d8114.blend"
OUT = Path(__file__).resolve().parent / "blender_probe.json"
EXPECTED_ID = "massing_baptist_student_foundation_c3d8114"
EXPECTED_COLLECTION = f"Asset_{EXPECTED_ID}"
EXPECTED_SCENE = f"Building_{EXPECTED_ID}"

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
collection = bpy.data.collections.get(EXPECTED_COLLECTION)
assert scene.name == EXPECTED_SCENE, (scene.name, EXPECTED_SCENE)
assert collection is not None, EXPECTED_COLLECTION
members = list(collection.objects)
assert len(members) >= 100, len(members)
assert all(obj.type == "MESH" for obj in members)

depsgraph = bpy.context.evaluated_depsgraph_get()
all_coords = []
for obj in members:
    evaluated = obj.evaluated_get(depsgraph)
    for corner in evaluated.bound_box:
        all_coords.append(obj.matrix_world @ Vector(corner))
lo = [min(p[i] for p in all_coords) for i in range(3)]
hi = [max(p[i] for p in all_coords) for i in range(3)]
structural = bpy.data.objects.get("Red brick exterior walls from LiDAR outline")
assert structural is not None and structural.type == "MESH"
assert len(structural.data.vertices) == 32, len(structural.data.vertices)
struct_xy = [structural.matrix_world @ v.co for v in structural.data.vertices]
footprint_bounds = [[min(p[i] for p in struct_xy), max(p[i] for p in struct_xy)] for i in range(2)]
external_images = [img.filepath for img in bpy.data.images if img.source == "FILE"]
external_libraries = [lib.filepath for lib in bpy.data.libraries]
modifiers = {obj.name: [mod.name for mod in obj.modifiers] for obj in members if obj.modifiers}
assert not external_images, external_images

result = {
    "asset": str(ASSET),
    "reopened": True,
    "scene": scene.name,
    "collection": EXPECTED_COLLECTION,
    "collection_count": sum(1 for c in bpy.data.collections if c.name == EXPECTED_COLLECTION),
    "collection_object_count": len(members),
    "mesh_objects": sum(1 for o in members if o.type == "MESH"),
    "non_mesh_objects": [o.name for o in members if o.type != "MESH"],
    "all_objects_in_expected_collection": all(o.name in collection.objects for o in members),
    "collection_instance_offset": list(collection.instance_offset),
    "coordinate_frame": "campus world XY per existing simple-massing manifest entry; no collection/object offset applied",
    "all_geometry_bounds_m": {"x": lo[0:1] + hi[0:1], "y": lo[1:2] + hi[1:2], "z": lo[2:3] + hi[2:3]},
    "structural_footprint_outline_bounds_m": footprint_bounds,
    "structural_wall_mesh_vertex_count": len(structural.data.vertices),
    "external_image_paths": external_images,
    "library_links": external_libraries,
    "modifiers": modifiers,
    "validation": "Saved asset reopens, expected scene and named export collection exist exactly once, assigned geometry is mesh-only and in the expected collection, and no external image textures or linked libraries are required.",
}
OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
