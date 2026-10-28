import bpy
import bmesh
import json
from pathlib import Path
from mathutils import Vector

root = Path(__file__).resolve().parents[2]
asset = root / "modular" / "buildings" / "massing_house_301841608_d56a4c4.blend"
report = Path(__file__).resolve().parent / "fresh_open_validation.json"

# The Blender process opens the assigned library before running this script.
assert Path(bpy.data.filepath).resolve() == asset.resolve(), bpy.data.filepath
collection = bpy.data.collections.get("Asset_massing_house_301841608_d56a4c4")
assert collection is not None
members = list(collection.objects)
assert len(members) == 1
obj = members[0]
assert obj.name == "House_301841608" and obj.type == "MESH"
world_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
minimum = [min(p[i] for p in world_corners) for i in range(3)]
maximum = [max(p[i] for p in world_corners) for i in range(3)]
bm = bmesh.new()
bm.from_mesh(obj.data)
non_manifold = sum(not edge.is_manifold for edge in bm.edges)
boundary_edges = sum(edge.is_boundary for edge in bm.edges)
bm.free()
images = [image.filepath for image in bpy.data.images if image.source == "FILE"]
libraries = [lib.filepath for lib in bpy.data.libraries]

result = {
    "status": "PASS",
    "fresh_open": True,
    "blender_version": bpy.app.version_string,
    "asset_path": str(asset),
    "collection": collection.name,
    "collection_object_count": len(members),
    "object": obj.name,
    "mesh_vertices": len(obj.data.vertices),
    "mesh_faces": len(obj.data.polygons),
    "world_bounds_m": {"min_xyz": minimum, "max_xyz": maximum},
    "world_dimensions_m": [maximum[i] - minimum[i] for i in range(3)],
    "material_names": [material.name if material else None for material in obj.data.materials],
    "non_manifold_edges": non_manifold,
    "boundary_edges": boundary_edges,
    "external_image_paths": images,
    "nested_library_paths": libraries,
    "source_feature_id": obj.get("source_feature_id"),
    "source_address": obj.get("source_address"),
    "height_evidence": obj.get("height_evidence"),
    "uncertainty": obj.get("uncertainty"),
}
report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print("AGD_FRESH_OPEN=" + json.dumps(result))
