"""Fresh-process structural and portability extraction for the Winifred R5 grade."""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/winifred_parker_hall.blend"
OUT = Path(__file__).resolve().parent / "independent_grade_r5_extract.json"
EXPECTED_SHA = "92fa120794470d93a253d04f35ca0852caea7d05982a5f4e02b285fd914045a9"

def bounds(obj):
    dg = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(dg)
    points = [evaluated.matrix_world @ Vector(corner) for corner in evaluated.bound_box]
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]

if Path(bpy.data.filepath).resolve() != ASSET.resolve():
    raise RuntimeError("Extractor must open the exact canonical Winifred asset")
sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
if sha != EXPECTED_SHA:
    raise RuntimeError(f"Asset SHA changed during grading: {sha}")
collection = bpy.data.collections.get("Asset_winifred_parker_hall")
root = bpy.data.objects.get("AssetRoot_winifred_parker_hall")
if collection is None or root is None:
    raise RuntimeError("Expected export collection or identity root missing")
objects = list(collection.all_objects)
meshes = [obj for obj in objects if obj.type == "MESH"]
used_materials = {material for obj in meshes for material in obj.data.materials if material}
missing_slots = [obj.name for obj in meshes if not obj.data.materials]
invalid_slots = [
    {"object": obj.name, "polygon": poly.index, "material_index": poly.material_index}
    for obj in meshes
    for poly in obj.data.polygons
    if poly.material_index >= len(obj.data.materials)
]
missing_images = []
unpacked_external_images = []
image_nodes = []
for material in used_materials:
    for node in material.node_tree.nodes if material.use_nodes and material.node_tree else []:
        if node.type == "TEX_IMAGE" and node.image:
            image_nodes.append({"material": material.name, "image": node.image.name, "filepath": node.image.filepath})
for image in bpy.data.images:
    if image.source == "FILE" and image.filepath:
        filepath = bpy.path.abspath(image.filepath)
        exists = Path(filepath).exists()
        if not exists and not image.packed_file:
            missing_images.append(image.filepath)
        if exists and not image.packed_file:
            unpacked_external_images.append(image.filepath)

shell = bpy.data.objects.get("Parker_GIS_Continuous_Upper_Shell")
ground = bpy.data.objects.get("Parker_GIS_Ground_Core_0")
roof = bpy.data.objects.get("Parker_GIS_Roof_Outline")
if not shell or not ground or not roof:
    raise RuntimeError("One or more R5 GIS replacement meshes are missing")

def mesh_snapshot(obj):
    world = obj.matrix_world
    vertices = [[float((world @ v.co)[0]), float((world @ v.co)[1]), float((world @ v.co)[2])] for v in obj.data.vertices]
    faces = [[int(i) for i in p.vertices] for p in obj.data.polygons]
    return {
        "name": obj.name,
        "vertices_world_local": vertices,
        "faces": faces,
        "bounds": bounds(obj),
        "material_names": [m.name for m in obj.data.materials if m],
    }

per_object_bounds = [bounds(obj) for obj in meshes]
aggregate_bounds = [
    [
        min(b[axis][0] for b in per_object_bounds),
        max(b[axis][1] for b in per_object_bounds),
    ]
    for axis in range(3)
]
asset_root_matrix = [[round(float(v), 9) for v in row] for row in root.matrix_world]
report = {
    "asset": str(ASSET),
    "sha256": sha,
    "fresh_process_reopen": True,
    "blender_version": bpy.app.version_string,
    "scene": bpy.context.scene.name,
    "collection": collection.name,
    "collection_object_count": len(objects),
    "mesh_count": len(meshes),
    "aggregate_mesh_bounds_local": aggregate_bounds,
    "non_mesh_types": {},
    "asset_root": root.name,
    "asset_root_world_matrix": asset_root_matrix,
    "used_material_count": len(used_materials),
    "used_material_names": sorted(m.name for m in used_materials),
    "materials": [
        {
            "name": material.name,
            "node_types": [node.type for node in material.node_tree.nodes] if material.use_nodes and material.node_tree else [],
            "base_color": [float(c) for c in material.diffuse_color],
            "roughness": float(material.roughness),
        }
        for material in sorted(used_materials, key=lambda m: m.name)
    ],
    "image_texture_nodes": image_nodes,
    "missing_material_slots": missing_slots,
    "invalid_material_indices": invalid_slots,
    "missing_external_images": missing_images,
    "unpacked_external_images": unpacked_external_images,
    "linked_libraries": [
        {"name": library.name, "filepath": library.filepath, "resolved": bpy.path.abspath(library.filepath)}
        for library in bpy.data.libraries
    ],
    "replacement_meshes": {
        "upper_shell": mesh_snapshot(shell),
        "ground_core": mesh_snapshot(ground),
        "roof": mesh_snapshot(roof),
    },
    "interior_objects": [
        obj.name for obj in objects
        if any(token in obj.name.lower() for token in ("suite", "bed", "bath", "lobby", "market", "starbucks", "desk", "study", "room", "reception", "corridor"))
    ],
    "fenestration_inventory": {
        "window_count": sum(obj.name.startswith("Parker_Win_") for obj in objects),
        "sill_count": sum(obj.name.startswith("Parker_Sill_") for obj in objects),
        "window_floor_indices": sorted({
            int(match.group(1))
            for obj in objects
            if obj.name.startswith("Parker_Win_")
            for match in [re.search(r"_F(\d+)_", obj.name)]
            if match
        }),
        "window_facade_counts": {
            facade: sum(obj.name.startswith(f"Parker_Win_{facade}_") for obj in objects)
            for facade in ("East", "West", "North", "South")
        },
    },
}
from collections import Counter
report["non_mesh_types"] = dict(Counter(obj.type for obj in objects if obj.type != "MESH"))
if len(objects) != 582 or len(meshes) != 581:
    raise RuntimeError(f"Unexpected export counts: {len(objects)} objects / {len(meshes)} meshes")
if missing_slots or invalid_slots or missing_images or bpy.data.libraries:
    raise RuntimeError("Portability/material validation failed")
if any(abs(asset_root_matrix[i][j] - (1.0 if i == j else 0.0)) > 1e-6 for i in range(4) for j in range(4)):
    raise RuntimeError("Asset root is not identity")
OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in report.items() if k != "replacement_meshes"}, indent=2, ensure_ascii=False))
