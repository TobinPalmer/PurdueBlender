"""Run with Blender -b <asset.blend> --python this_file.py."""
import bpy
import json
import bmesh
from pathlib import Path

root = Path(__file__).resolve().parents[2]
asset = root / "modular/buildings/massing_animal_holding_facility_4733f46.blend"
out = Path(__file__).resolve().parent / "reopen_verification.json"
collection_name = "Asset_massing_animal_holding_facility_4733f46"
collection = bpy.data.collections.get(collection_name)
assert collection is not None
members = list(collection.objects)
assert len(members) == 1
obj = members[0]
assert obj.name == "Animal Holding Facility" and obj.type == "MESH"
depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated = obj.evaluated_get(depsgraph)
mesh = evaluated.to_mesh()
assert len(mesh.vertices) > 0 and len(mesh.polygons) > 0
topology = bmesh.new()
topology.from_mesh(obj.data)
non_manifold_edges = [edge.index for edge in topology.edges if not edge.is_manifold]
boundary_edges = [edge.index for edge in topology.edges if edge.is_boundary]
topology.free()
assert not non_manifold_edges, f"Non-manifold edges: {non_manifold_edges}"
assert not boundary_edges, f"Boundary edges: {boundary_edges}"
world_points = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
bounds = [[min(v[i] for v in world_points), max(v[i] for v in world_points)] for i in range(3)]
evaluated.to_mesh_clear()
result = {
    "opened_asset": str(asset),
    "scene": bpy.context.scene.name,
    "collection": collection.name,
    "collection_object_count": len(members),
    "object": obj.name,
    "type": obj.type,
    "mesh_vertices": len(obj.data.vertices),
    "mesh_faces": len(obj.data.polygons),
    "topology": {
        "non_manifold_edge_count": len(non_manifold_edges),
        "boundary_edge_count": len(boundary_edges),
        "result": "PASS"
    },
    "modifiers": [m.name for m in obj.modifiers],
    "evaluated_bounds_world_m": bounds,
    "portable_material_images": [img.filepath for img in bpy.data.images if img.source == "FILE"],
    "result": "PASS"
}
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
