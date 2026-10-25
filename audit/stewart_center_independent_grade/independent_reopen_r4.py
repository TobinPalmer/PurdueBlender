"""Independent saved-asset reopen check for Stewart Center R4."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/stewart_center.blend"
OUTPUT = Path(__file__).resolve().parent / "independent_reopen_r4.json"
EXPECTED = "a10c5e28e0e90f83352e871c3deda5a747198d2398969f4491c756cf95a72b9a"
COLLECTION_NAME = "Asset_stewart_center"
ROOT_NAME = "AssetRoot_stewart_center"

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
collection = bpy.data.collections.get(COLLECTION_NAME)
root = bpy.data.objects.get(ROOT_NAME)
if collection is None or root is None:
    raise RuntimeError("Expected Stewart asset collection/root missing after fresh reopen")
objects = list(collection.all_objects)
meshes = [obj for obj in objects if obj.type == "MESH"]
materialless = [obj.name for obj in meshes if not obj.data.materials or any(m is None for m in obj.data.materials)]
missing_images = []
for image in bpy.data.images:
    if image.source == "FILE" and image.filepath and not image.packed_file:
        path = Path(bpy.path.abspath(image.filepath, library=image.library))
        if not path.exists():
            missing_images.append({"image": image.name, "path": str(path)})

cache = {}
def world_matrix(obj):
    if obj in cache:
        return cache[obj]
    matrix = obj.matrix_local.copy()
    if obj.parent is not None:
        matrix = world_matrix(obj.parent) @ matrix
    cache[obj] = matrix
    return matrix

geometry = [obj for obj in objects if obj.type in {"MESH", "CURVE", "FONT"}]
points = [world_matrix(obj) @ Vector(corner) for obj in geometry for corner in obj.bound_box]
bounds = [[min(point[i] for point in points), max(point[i] for point in points)] for i in range(3)] if points else []
asset_sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
result = {
    "asset": "modular/buildings/stewart_center.blend",
    "sha256": asset_sha,
    "expected_sha256": EXPECTED,
    "hash_matches_expected": asset_sha == EXPECTED,
    "fresh_reopen": True,
    "blender_version": bpy.app.version_string,
    "collection": COLLECTION_NAME,
    "collection_object_count": len(objects),
    "mesh_count": len(meshes),
    "material_count": len(bpy.data.materials),
    "materialless_meshes": materialless,
    "missing_external_images": missing_images,
    "root": {"name": root.name, "location": list(root.location), "rotation_euler": list(root.rotation_euler), "scale": list(root.scale)},
    "root_matrix_world": [[float(root.matrix_world[r][c]) for c in range(4)] for r in range(4)],
    "asset_bounds_local_m": bounds,
    "structural_wall_count": sum(1 for obj in objects if obj.name.startswith("Stewart_GIS_Shell")),
    "scene_name": bpy.context.scene.name if bpy.context.scene else None,
}
if asset_sha != EXPECTED or len(objects) != 2764 or len(meshes) != 2752:
    raise RuntimeError(f"R4 source file differs from the reviewed revision: {result}")
if materialless or missing_images:
    raise RuntimeError(f"R4 asset portability/material check failed: {result}")
OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))
