"""Run with Blender 4.5: blender -b <asset.blend> --python blender_probe.py"""
import bpy
import bmesh
import json
from pathlib import Path

collection_name = "Asset_massing_animal_holding_facility_4733f46"
collection = bpy.data.collections.get(collection_name)
if collection is None:
    raise RuntimeError(f"Missing expected collection {collection_name}")
objects = list(collection.objects)
if len(objects) != 1 or objects[0].type != "MESH":
    raise RuntimeError(f"Unexpected collection contents: {[(o.name, o.type) for o in objects]}")
obj = objects[0]
bm = bmesh.new()
bm.from_mesh(obj.data)
probe = {
    "scene": bpy.context.scene.name,
    "collection": collection.name,
    "collection_object_count": len(objects),
    "object": obj.name,
    "object_type": obj.type,
    "mesh_vertex_count": len(obj.data.vertices),
    "mesh_edge_count": len(obj.data.edges),
    "mesh_face_count": len(obj.data.polygons),
    "boundary_edge_count": sum(edge.is_boundary for edge in bm.edges),
    "nonmanifold_edge_count": sum(not edge.is_manifold for edge in bm.edges),
    "dimensions_m": list(obj.dimensions),
    "bounds_xyz_m": [[min(v.co[i] for v in obj.data.vertices), max(v.co[i] for v in obj.data.vertices)] for i in range(3)],
    "material_face_counts": {str(i): sum(p.material_index == i for p in obj.data.polygons) for i in range(len(obj.data.materials))},
    "material_names": [m.name if m else None for m in obj.data.materials],
    "modifier_count": len(obj.modifiers),
    "image_dependencies": [im.filepath for im in bpy.data.images if im.source == "FILE"],
    "mesh_is_closed_manifold": all(edge.is_manifold for edge in bm.edges),
}
bm.free()
out = Path(__file__).resolve().parent / "blender_probe.json"
out.write_text(json.dumps(probe, indent=2) + "\n", encoding="utf-8")
print("AHF_INDEPENDENT_BLENDER_PROBE=" + json.dumps(probe, sort_keys=True))
