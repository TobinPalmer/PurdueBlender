"""Fresh-process, read-only integrity extraction for frozen Tarkington R4."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "audit" / "tarkington_hall"
EXPECTED_SHA = "b844a77e35ad44bf722ea0432ed40dc47a6b01fff24c095cbabf68e760f87065"
ASSET = OUT / "tarkington_hall_r4_candidate.blend"
COLLECTION_NAME = "Asset_tarkington_hall"
ROOT_NAME = "AssetRoot_tarkington_hall"


def close(a, b, tol=1e-6):
    return abs(float(a) - float(b)) <= tol


if Path(bpy.data.filepath).resolve() != ASSET.resolve():
    raise RuntimeError(f"Wrong file opened: {bpy.data.filepath}")
actual_sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
if actual_sha != EXPECTED_SHA:
    raise RuntimeError(f"Candidate SHA changed: {actual_sha}")

collection = bpy.data.collections.get(COLLECTION_NAME)
root_obj = bpy.data.objects.get(ROOT_NAME)
if collection is None or root_obj is None:
    raise RuntimeError("Expected export collection/root is missing")
objects = list(collection.objects)
meshes = [obj for obj in objects if obj.type == "MESH"]
object_names = {obj.name for obj in objects}
connectors = [obj for obj in bpy.data.objects if "Connector" in obj.name]
connector_names = {obj.name for obj in connectors}
outside_export = sorted(connector_names - object_names)
parent_errors = sorted(obj.name for obj in connectors if obj.name in object_names and obj.parent != root_obj)
materialless = sorted(obj.name for obj in meshes if not any(mat for mat in obj.data.materials))
nonfinite = sorted(
    obj.name for obj in meshes
    if any(not all(math.isfinite(float(value)) for value in vert.co) for vert in obj.data.vertices)
)
duplicate_names = sorted(name for name in object_names if sum(obj.name == name for obj in objects) > 1)
invalid_material_indices = sorted(
    obj.name for obj in meshes
    if any(poly.material_index >= len(obj.data.materials) for poly in obj.data.polygons)
)
external_images = []
for image in bpy.data.images:
    if image.source == "FILE" and image.users and not image.packed_file:
        path = Path(bpy.path.abspath(image.filepath))
        if not path.exists():
            external_images.append(str(path))
foreign_libraries = sorted(
    lib.filepath for lib in bpy.data.libraries
    if "tarkington_hall_r4_candidate.blend" not in lib.filepath
)
root_identity = all(close(value, 1.0) for value in root_obj.scale) and all(
    close(value, 0.0) for value in root_obj.rotation_euler
)

points = [obj.matrix_world @ vert.co for obj in meshes for vert in obj.data.vertices]
if not points:
    raise RuntimeError("No mesh vertices found")
bounds = [
    [min(float(v[axis]) for v in points), max(float(v[axis]) for v in points)]
    for axis in range(3)
]

audit = json.loads((ROOT / "audit" / "master_building_audit.json").read_text(encoding="utf-8"))
record = next(item for item in audit["records"] if item.get("id") == "tarkington_hall")
base_shell_names = set(record["shell_candidates"])
connector_shell_tokens = (
    "Brick_Shaft", "Limestone_Base", "Limestone_Belt_", "Roof_Membrane", "Roof_Parapet"
)
shell_objects = []
for obj in meshes:
    name = obj.name
    connector_shell = (
        ("Connector" in name or "South_Lobby_Core" in name)
        and any(token in name for token in connector_shell_tokens)
    )
    if name in base_shell_names or connector_shell:
        shell_objects.append({
            "name": name,
            "vertices_xy": [
                [float((obj.matrix_world @ vert.co).x), float((obj.matrix_world @ vert.co).y)]
                for vert in obj.data.vertices
            ],
        })

report = {
    "candidate": str(ASSET),
    "sha256": actual_sha,
    "blender_version": bpy.app.version_string,
    "scene": bpy.context.scene.name,
    "collection": COLLECTION_NAME,
    "collection_object_count": len(objects),
    "mesh_count": len(meshes),
    "mesh_vertex_count": sum(len(obj.data.vertices) for obj in meshes),
    "mesh_face_count": sum(len(obj.data.polygons) for obj in meshes),
    "connector_object_count_database": len(connectors),
    "connector_objects_in_export": len(connector_names & object_names),
    "connector_objects_outside_export": outside_export,
    "connector_parent_errors": parent_errors,
    "used_material_names": sorted({mat.name for obj in meshes for mat in obj.data.materials if mat}),
    "materialless_meshes": materialless,
    "invalid_material_indices": invalid_material_indices,
    "nonfinite_meshes": nonfinite,
    "duplicate_object_names": duplicate_names,
    "missing_external_images": sorted(external_images),
    "linked_libraries": [lib.filepath for lib in bpy.data.libraries],
    "asset_root_identity_transform": root_identity,
    "aggregate_mesh_bounds_local_m": bounds,
    "shell_object_count_for_independent_footprint": len(shell_objects),
    "source_shell_candidate_count": len(base_shell_names),
}
(OUT / "independent_grade_r4_reopen.json").write_text(
    json.dumps(report, indent=2) + "\n", encoding="utf-8"
)
(OUT / "independent_grade_r4_shell_vertices.json").write_text(
    json.dumps({
        "asset_sha256": actual_sha,
        "objects": shell_objects,
        "selection_method": (
            "Read-only fresh Blender reopen. Source shell candidate names from master_building_audit.json; "
            "plus only named connector/core structural shell components. Decorative, glazing, furniture, and paths excluded."
        ),
        "coordinates": "Asset-root local XY metres; source polygon transformed by project-local conversion then marker origin subtracted.",
    }, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(report, indent=2))
