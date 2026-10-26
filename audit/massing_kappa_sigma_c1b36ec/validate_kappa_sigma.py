"""Reopen and verify the Kappa Sigma modular asset with Blender's bpy API."""
import json
from pathlib import Path

import bpy
import bmesh

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_kappa_sigma_c1b36ec"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
SOURCE = ROOT / "audit" / ASSET_ID / "sources" / "purdue_gis_fid804_2026-10-26.json"
OUTPUT = ROOT / "audit" / ASSET_ID / "reopen_validation.json"

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
collection = bpy.data.collections.get(f"Asset_{ASSET_ID}")
assert scene.name == f"Building_{ASSET_ID}", scene.name
assert collection is not None
assert [obj.name for obj in collection.objects] == ["Kappa Sigma"]
obj = collection.objects[0]
assert obj.type == "MESH"
assert obj.location.length < 1e-6
assert max(abs(v - 1.0) for v in obj.scale) < 1e-6
assert max(abs(v) for v in obj.rotation_euler) < 1e-6
assert len(obj.modifiers) == 0

depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated = obj.evaluated_get(depsgraph)
mesh = evaluated.to_mesh()
bmesh_mesh = bmesh.new()
bmesh_mesh.from_mesh(mesh)
world_vertices = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
bounds = [[min(v[i] for v in world_vertices), max(v[i] for v in world_vertices)] for i in range(3)]
source = json.loads(SOURCE.read_text(encoding="utf-8"))
ring = source["features"][0]["geometry"]["rings"][0]
if ring[0] == ring[-1]:
    ring = ring[:-1]
origin_lat = 40.4274
target = [((lon + 86.9137) * 111412.84 * __import__("math").cos(__import__("math").radians(origin_lat)),
           (lat - 40.4274) * 111040.0) for lon, lat in ring]
bottom_faces = [poly for poly in mesh.polygons
                if len(poly.vertices) == len(target)
                and all(abs(mesh.vertices[index].co.z) < 1e-6 for index in poly.vertices)]
assert bottom_faces, "No bottom perimeter face corresponding to the source footprint"
perimeter_face = bottom_faces[0]
saved_ring = [(mesh.vertices[index].co.x, mesh.vertices[index].co.y) for index in perimeter_face.vertices]
target_set = {(round(x, 2), round(y, 2)) for x, y in target}
saved_set = {(round(x, 2), round(y, 2)) for x, y in saved_ring}
if saved_set != target_set:
    raise AssertionError(json.dumps({
        "message": "Saved bottom perimeter differs from projected Purdue GIS ring",
        "target_count": len(target_set),
        "saved_count": len(saved_set),
        "target_only": sorted(target_set - saved_set)[:5],
        "saved_only": sorted(saved_set - target_set)[:5],
        "bottom_face_vertex_count": len(perimeter_face.vertices),
    }))
external_images = [image.filepath for image in bpy.data.images if image.source == "FILE"]
assert not external_images, external_images
assert len([obj for obj in bpy.data.objects if obj.type == "MESH"]) == 1

result = {
    "status": "passed",
    "blender_version": bpy.app.version_string,
    "reopened_asset_path": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
    "scene": scene.name,
    "collection": collection.name,
    "collection_object_names": [item.name for item in collection.objects],
    "object_type": obj.type,
    "object_location": list(obj.location),
    "object_rotation_radians": list(obj.rotation_euler),
    "object_scale": list(obj.scale),
    "modifier_count": len(obj.modifiers),
    "evaluated_bounds_world_m": bounds,
    "mesh_vertices": len(mesh.vertices),
    "mesh_edges": len(mesh.edges),
    "mesh_faces": len(mesh.polygons),
    "boundary_edges": sum(edge.is_boundary for edge in bmesh_mesh.edges),
    "non_manifold_edges": sum(not edge.is_manifold for edge in bmesh_mesh.edges),
    "wire_edges": sum(edge.is_wire for edge in bmesh_mesh.edges),
    "source_footprint_vertex_count": len(target),
        "source_footprint_match": "bottom boundary vertex set matches transformed FID 804 ring to 0.01 m rounding",
    "external_image_dependencies": external_images,
    "asset_collection_objects": len(collection.objects),
    "all_mesh_objects_in_library": len([item for item in bpy.data.objects if item.type == "MESH"]),
}
OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print("KAPPA_SIGMA_REOPEN_VALIDATION=" + json.dumps(result, sort_keys=True))
bmesh_mesh.free()
evaluated.to_mesh_clear()
