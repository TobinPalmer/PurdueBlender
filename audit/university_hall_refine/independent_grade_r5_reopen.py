"""Independent fresh-process exact-SHA reopen for University Hall R5."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/university_hall.blend"
REPORT = ROOT / "audit/university_hall_refine/independent_grade_r5_reopen.json"
EXPECTED_SHA = "8f10d54f13262fb4f4c847e41072df28ed2f607d2715171db4a2ff3789e0c05b"
COLLECTION_NAME = "Asset_university_hall"
ROOT_NAME = "AssetRoot_university_hall"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if Path(bpy.data.filepath).resolve() != ASSET.resolve():
    raise RuntimeError("Run Blender with university_hall.blend loaded before this script")
actual_sha = sha256(ASSET)
if actual_sha != EXPECTED_SHA:
    raise RuntimeError(f"Asset hash mismatch: {actual_sha}")
collection = bpy.data.collections.get(COLLECTION_NAME)
root = bpy.data.objects.get(ROOT_NAME)
if collection is None or root is None:
    raise RuntimeError("Expected exported collection or identity root is missing")
objects = list(collection.all_objects)
meshes = [obj for obj in objects if obj.type == "MESH"]
materialless = sorted(obj.name for obj in meshes if len(obj.material_slots) == 0)
invalid_slots = []
used_materials = set()
for obj in meshes:
    for slot in obj.material_slots:
        if slot.material is None:
            invalid_slots.append(obj.name)
        else:
            used_materials.add(slot.material.name)
missing_images = []
for image in bpy.data.images:
    if image.source == "FILE" and image.filepath:
        path = Path(bpy.path.abspath(image.filepath))
        if not path.exists() and not image.packed_file:
            missing_images.append({"image": image.name, "path": str(path)})
linked_libraries = sorted(library.filepath for library in bpy.data.libraries if library.filepath)
depsgraph = bpy.context.evaluated_depsgraph_get()
mins = [float("inf")] * 3
maxs = [float("-inf")] * 3
for obj in meshes:
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        matrix = evaluated.matrix_world
        for vertex in mesh.vertices:
            point = matrix @ vertex.co
            for axis in range(3):
                mins[axis] = min(mins[axis], float(point[axis]))
                maxs[axis] = max(maxs[axis], float(point[axis]))
    finally:
        evaluated.to_mesh_clear()
bounds = [[mins[i], maxs[i]] for i in range(3)]
column_prefix = "UNIV_R5_ReclaimedDisplayColumn_"
column_objects = [obj.name for obj in objects if obj.name.startswith(column_prefix)]
column_assemblies = set()
for name in column_objects:
    suffix_parts = name[len(column_prefix):].split("_")
    group_size = 2 if suffix_parts[0] in {"Ground", "Third"} else 1
    column_assemblies.add("_".join(suffix_parts[:group_size]))
result = {
    "review": "Independent fresh-process Blender 5.2.3 LTS reopen of the frozen R5 asset",
    "asset": str(ASSET),
    "sha256": actual_sha,
    "expected_sha256": EXPECTED_SHA,
    "hash_matches_candidate": actual_sha == EXPECTED_SHA,
    "blender_version": bpy.app.version_string,
    "scene": bpy.context.scene.name,
    "scene_object_count": len(bpy.context.scene.objects),
    "export_collection": COLLECTION_NAME,
    "export_collection_object_count": len(objects),
    "mesh_count": len(meshes),
    "root": {
        "name": root.name,
        "location": list(root.location),
        "rotation_euler": list(root.rotation_euler),
        "scale": list(root.scale),
        "identity_matrix": all(
            abs(root.matrix_world[row][column] - (1.0 if row == column else 0.0)) < 1e-6
            for row in range(4) for column in range(4)
        ),
    },
    "evaluated_bounds_local_m_axis_major": bounds,
    "used_material_count": len(used_materials),
    "used_material_names": sorted(used_materials),
    "materialless_meshes": materialless,
    "invalid_material_slot_meshes": sorted(set(invalid_slots)),
    "missing_external_images": missing_images,
    "linked_libraries": linked_libraries,
    "r5_geometry_counts": {
        "display_column_assembly_labels": sorted(column_assemblies),
        "display_column_assembly_count": len(column_assemblies),
        "display_column_component_objects": len(column_objects),
        "gallery_objects": sum(1 for obj in objects if "Gallery" in obj.name or "Overlook" in obj.name),
        "stair_objects": sum(1 for obj in objects if "Stair" in obj.name),
        "roof_objects": sum(1 for obj in objects if "Roof" in obj.name or "Dormer" in obj.name or "Slate" in obj.name),
    },
    "review_render_files": [
        "ground_oblique_r5.png",
        "east_elevation_r5.png",
        "entry_ground_r5.png",
        "interior_cutaway_r5.png",
    ],
    "assessment_limits": [
        "Fresh reopen verifies saved asset integrity only; master placement is not graded.",
        "Footprint residual evidence references campus-map FID 213, not a surveyed wall perimeter.",
        "Roof, tower, windows, interior display-column positions and circulation remain image- or program-estimated absent measured drawings.",
    ],
}
REPORT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))
