"""Independent Blender reopen and manifest check for Owen Hall R2."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/owen_hall.blend"
MANIFEST = ROOT / "modular/manifest.json"
OUT = Path(__file__).with_name("independent_reopen_r3.json")

collection = bpy.data.collections.get("Asset_owen_hall")
assert collection is not None
objects = list(collection.all_objects)
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
entry = next(item for item in manifest["assets"] if item["id"] == "owen_hall")
root = bpy.data.objects.get("AssetRoot_owen_hall")
depsgraph = bpy.context.evaluated_depsgraph_get()
points = []
mesh_objects = [obj for obj in objects if obj.type == "MESH"]
for obj in mesh_objects:
    evaluated = obj.evaluated_get(depsgraph)
    for corner in evaluated.bound_box:
        points.append(obj.matrix_world @ Vector(corner))

image_refs = []
for image in bpy.data.images:
    if image.source == "FILE" and image.packed_file is None:
        image_refs.append({"name": image.name, "path": image.filepath})
library_refs = [lib.filepath for lib in bpy.data.libraries]
node_materials = {
    slot.material.name
    for obj in mesh_objects
    for slot in obj.material_slots
    if slot.material is not None and slot.material.use_nodes
}
unassigned_meshes = [
    obj.name for obj in mesh_objects
    if not obj.material_slots or any(slot.material is None for slot in obj.material_slots)
]
actual_names = sorted(obj.name for obj in objects)
manifest_names = sorted(entry.get("objects", []))
local_bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]
origin = entry["placement_origin_xy_m"]
world_bounds = [
    [local_bounds[0][0] + origin[0], local_bounds[0][1] + origin[0]],
    [local_bounds[1][0] + origin[1], local_bounds[1][1] + origin[1]],
    local_bounds[2],
]
base = bpy.data.objects.get("Owen_GIS_Limestone_Base")
base_mesh = base.evaluated_get(depsgraph).to_mesh() if base else None
boundary_uses = {}
if base_mesh is not None:
    for face in base_mesh.polygons:
        if not all(abs(base_mesh.vertices[idx].co.z) < 1e-7 for idx in face.vertices):
            continue
        for edge in face.edge_keys:
            edge = tuple(sorted(edge))
            boundary_uses[edge] = boundary_uses.get(edge, 0) + 1
neighbors = {}
for (a, b), uses in boundary_uses.items():
    if uses == 1:
        neighbors.setdefault(a, []).append(b)
        neighbors.setdefault(b, []).append(a)
base_outline = []
if neighbors and all(len(items) == 2 for items in neighbors.values()):
    start = min(neighbors)
    previous = None
    current = start
    while True:
        point = base.matrix_world @ base_mesh.vertices[current].co
        base_outline.append([float(point.x), float(point.y)])
        nxt = next(idx for idx in neighbors[current] if idx != previous)
        if nxt == start:
            break
        previous, current = current, nxt
if base_mesh is not None:
    base.evaluated_get(depsgraph).to_mesh_clear()
result = {
    "asset": "modular/buildings/owen_hall.blend",
    "asset_sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
    "blender_version": bpy.app.version_string,
    "scene_names": [scene.name for scene in bpy.data.scenes],
    "collection": collection.name,
    "collection_object_count": len(objects),
    "object_type_counts": {kind: sum(obj.type == kind for obj in objects)
                            for kind in sorted({obj.type for obj in objects})},
    "asset_root": root.name if root else None,
    "asset_root_location": list(root.location) if root else None,
    "asset_root_world_translation": list(root.matrix_world.translation) if root else None,
    "asset_root_rotation": list(root.rotation_euler) if root else None,
    "asset_root_scale": list(root.scale) if root else None,
    "evaluated_mesh_bounds_local_m": local_bounds,
    "evaluated_mesh_bounds_world_m": world_bounds,
    "manifest_bounds_world_m": entry["bounds_world_m"],
    "bounds_match_within_0_001m": all(
        abs(world_bounds[axis][side] - entry["bounds_world_m"][axis][side]) <= 0.001
        for axis in range(3) for side in range(2)
    ),
    "manifest_object_count": entry["object_count"],
    "manifest_names_match": actual_names == manifest_names,
    "manifest_names_missing": sorted(set(actual_names) - set(manifest_names)),
    "manifest_names_extra": sorted(set(manifest_names) - set(actual_names)),
    "mesh_count": len(mesh_objects),
    "mesh_objects_with_unassigned_materials": unassigned_meshes,
    "unique_node_material_count": len(node_materials),
    "missing_external_images": image_refs,
    "external_libraries": library_refs,
    "placement_origin_xy_m": origin,
    "placement_transform": entry.get("placement_transform"),
    "footprint_base_mesh": base.name if base else None,
    "footprint_vertex_xy_local_m": base_outline,
    "master_library_refresh_record": "No coordinator refresh for the current asset hash; master integration remains pending.",
}
OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in result.items() if k not in {"manifest_names_missing", "manifest_names_extra"}}, indent=2))
