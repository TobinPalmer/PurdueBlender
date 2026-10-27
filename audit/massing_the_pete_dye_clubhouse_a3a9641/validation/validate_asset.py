"""Read-only reopen audit for the Pete Dye Clubhouse modular asset."""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

root = Path(bpy.data.filepath).parents[2]
source = json.loads((root / "audit/massing_the_pete_dye_clubhouse_a3a9641/sources/osm_way_1319175917.json").read_text())
coords = [(n["lon"], n["lat"]) for n in source["nodes"]]
coords = coords[:-1] if coords[0] == coords[-1] else coords
expected = [((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
             (lat - 40.4274) * 111040.0) for lon, lat in coords]

scene = bpy.context.scene
collection = bpy.data.collections["Asset_massing_the_pete_dye_clubhouse_a3a9641"]
foundation = bpy.data.objects["PDC structural foundation footprint"]
foot = [foundation.matrix_world @ foundation.data.vertices[i].co for i in range(4)]
footprint_error = max(math.hypot(foot[i].x - expected[i][0], foot[i].y - expected[i][1])
                      for i in range(4))
depsgraph = bpy.context.evaluated_depsgraph_get()
all_points = []
modifier_count = 0
mesh_count = 0
non_mesh = []
for obj in collection.objects:
    modifier_count += len(obj.modifiers)
    if obj.type != "MESH":
        non_mesh.append([obj.name, obj.type])
        continue
    mesh_count += 1
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    all_points.extend(obj.matrix_world @ v.co for v in mesh.vertices)
    evaluated.to_mesh_clear()

result = {
    "scene": scene.name,
    "collection": collection.name,
    "asset_path": bpy.data.filepath,
    "collection_object_count": len(collection.objects),
    "scene_object_count": len(scene.objects),
    "mesh_object_count": mesh_count,
    "modifier_count": modifier_count,
    "non_mesh_objects": non_mesh,
    "collection_instance_offset": list(collection.instance_offset),
    "source_footprint_vertex_count": len(expected),
    "footprint_match_error_m": footprint_error,
    "footprint_vertices_xy_m": [[round(v.x, 4), round(v.y, 4)] for v in foot],
    "evaluated_asset_bounds_world_m": [[min(v[i] for v in all_points), max(v[i] for v in all_points)] for i in range(3)],
    "roof_peak_estimate_m": max(v.z for v in all_points),
    "portable_image_paths": all(not im.filepath or im.packed_file is not None or im.filepath.startswith("//") for im in bpy.data.images),
}
print("PDC_REOPEN_VALIDATION " + json.dumps(result, indent=2))
(root / "audit/massing_the_pete_dye_clubhouse_a3a9641/validation/reopen_validation.json").write_text(
    json.dumps(result, indent=2) + "\n", encoding="utf-8")
