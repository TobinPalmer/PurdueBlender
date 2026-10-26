"""Independent, read-only inspection of the canonical Tarkington Hall library."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/tarkington_hall.blend"
OUT = Path(__file__).resolve().parent / "independent_reopen_r2.json"
EXPECTED_SHA = "75aad771c9da9e454bbea76ef48852519fa58997747547f9120977e81a6aede5"

if Path(bpy.data.filepath).resolve() != ASSET.resolve():
    raise RuntimeError(f"Expected canonical asset {ASSET}, got {bpy.data.filepath}")
sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
if sha != EXPECTED_SHA:
    raise RuntimeError(f"Canonical SHA mismatch: {sha}")

scene = bpy.context.scene
collection = bpy.data.collections.get("Asset_tarkington_hall")
root = bpy.data.objects.get("AssetRoot_tarkington_hall")
if collection is None or root is None:
    raise RuntimeError("Expected named export collection and root object")
objects = list(collection.all_objects)
meshes = [obj for obj in objects if obj.type == "MESH"]
nonfinite = sorted({
    obj.name
    for obj in meshes
    if any(not all(math.isfinite(float(c)) for c in vert.co) for vert in obj.data.vertices)
})
materialless = sorted(obj.name for obj in meshes if not any(mat is not None for mat in obj.data.materials))
invalid_material_indices = sorted(
    obj.name for obj in meshes
    if any(poly.material_index >= len(obj.data.materials) for poly in obj.data.polygons)
)
missing_images = []
for image in bpy.data.images:
    if image.source == "FILE" and image.users and image.packed_file is None:
        try:
            resolved = Path(bpy.path.abspath(image.filepath, library=image.library)).resolve()
        except Exception:
            resolved = Path()
        if not resolved.exists():
            missing_images.append(image.name)

world_points = [
    obj.matrix_world @ Vector(corner)
    for obj in meshes
    for corner in obj.bound_box
]
world_bounds = [[
    min(float(v[i]) for v in world_points),
    max(float(v[i]) for v in world_points),
] for i in range(3)]
room = bpy.data.objects.get("Tark_Dorm_Room118_Floor")
root_identity = (
    all(abs(float(v) - 1.0) <= 1e-6 for v in root.scale)
    and all(abs(float(v)) <= 1e-6 for v in root.rotation_euler)
)
report = {
    "fresh_process_reopen": True,
    "asset": str(ASSET),
    "sha256": sha,
    "blender_version": bpy.app.version_string,
    "scene": scene.name,
    "export_collection": collection.name,
    "object_count": len(objects),
    "mesh_count": len(meshes),
    "used_material_count": sum(1 for mat in bpy.data.materials if mat.users),
    "root_exists": root is not None,
    "root_transform_identity": root_identity,
    "collection_object_count": len(objects),
    "nonfinite_meshes": nonfinite,
    "materialless_meshes": materialless,
    "invalid_material_meshes": invalid_material_indices,
    "missing_external_images": sorted(missing_images),
    "linked_libraries": sorted({
        lib.filepath for lib in bpy.data.libraries
        if Path(bpy.path.abspath(lib.filepath)).resolve() != ASSET.resolve()
    }),
    "world_bounds_xyz_m": world_bounds,
    "room118_floor_dimensions_m": list(map(float, room.dimensions)) if room else None,
}
OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
