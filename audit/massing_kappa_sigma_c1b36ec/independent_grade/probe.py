import bpy
import json
import os
import math

root = os.path.abspath(os.path.join(os.path.dirname(bpy.data.filepath), "..", ".."))
audit = os.path.join(root, "audit", "massing_kappa_sigma_c1b36ec")
src_path = os.path.join(audit, "sources", "purdue_gis_fid804_2026-10-26.json")
with open(src_path, encoding="utf-8") as f:
    source = json.load(f)

scene = bpy.context.scene
collection = bpy.data.collections.get("Asset_massing_kappa_sigma_c1b36ec")
objects = list(collection.objects) if collection else []
mesh = next((o for o in objects if o.type == "MESH"), None)
result = {
    "asset_path": bpy.data.filepath,
    "blender_version": bpy.app.version_string,
    "scene": scene.name,
    "expected_scene": "Building_massing_kappa_sigma_c1b36ec",
    "scene_match": scene.name == "Building_massing_kappa_sigma_c1b36ec",
    "expected_collection_present": collection is not None,
    "collection_objects": [o.name for o in objects],
    "expected_object_present": any(o.name == "Kappa Sigma" for o in objects),
    "all_library_objects": [o.name for o in bpy.data.objects],
    "external_images": [i.filepath for i in bpy.data.images if i.source == "FILE" and i.filepath],
}
if mesh:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = mesh.evaluated_get(depsgraph)
    evaluated_mesh = evaluated.to_mesh()
    world_vertices = [evaluated.matrix_world @ v.co for v in evaluated_mesh.vertices]
    ring = source["features"][0]["geometry"]["rings"][0]
    source_xy = [
        ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)), (lat - 40.4274) * 111040.0)
        for lon, lat in ring[:-1]
    ]
    bottom = [(v.x, v.y) for v in world_vertices if abs(v.z) < 1e-5]
    nearest = [min(math.hypot(x-sx, y-sy) for x, y in bottom) for sx, sy in source_xy]
    result.update({
        "object_type": mesh.type,
        "transform": {"location": list(mesh.location), "rotation": list(mesh.rotation_euler), "scale": list(mesh.scale)},
        "modifier_count": len(mesh.modifiers),
        "vertex_count": len(evaluated_mesh.vertices),
        "edge_count": len(evaluated_mesh.edges),
        "polygon_count": len(evaluated_mesh.polygons),
        "bounds": [[min(v[i] for v in world_vertices), max(v[i] for v in world_vertices)] for i in range(3)],
        "bounds_xy_dimensions": [max(v.x for v in world_vertices)-min(v.x for v in world_vertices), max(v.y for v in world_vertices)-min(v.y for v in world_vertices)],
        "source_ring_vertices": len(source_xy),
        "base_vertices_at_ground": len(bottom),
        "source_ring_nearest_vertex_error_max_m": max(nearest),
        "source_ring_all_vertices_within_0_01m": max(nearest) <= 0.01,
    })
    evaluated.to_mesh_clear()
with open(os.path.join(os.path.dirname(__file__), "blender_probe.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
