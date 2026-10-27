"""Compare a pre-localized graded candidate with the placed local library.

Start Blender on the pre-localization candidate, then run:
  blender -b graded_candidate.blend --python compare_localized_geometry.py -- LOCAL_ASSET ORIGIN_X ORIGIN_Y ASSET_COLLECTION OUTPUT_JSON
"""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
if len(args) != 5:
    raise SystemExit("Expected LOCAL_ASSET ORIGIN_X ORIGIN_Y ASSET_COLLECTION OUTPUT_JSON")
local_asset = Path(args[0]).resolve()
origin = Vector((float(args[1]), float(args[2]), 0.0))
collection_name = args[3]
output_path = Path(args[4]).resolve()
source_asset = Path(bpy.data.filepath).resolve()


def evaluated_points():
    collection = bpy.data.collections.get(collection_name)
    if collection is None:
        raise RuntimeError(f"Missing collection {collection_name}")
    depsgraph = bpy.context.evaluated_depsgraph_get()
    out = {}
    for obj in collection.all_objects:
        if obj.type not in {"MESH", "CURVE", "FONT", "SURFACE", "META"}:
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
            out[obj.name] = {
                "points": points,
                "vertex_count": len(mesh.vertices),
                "polygon_count": len(mesh.polygons),
            }
        finally:
            evaluated.to_mesh_clear()
    return out


source = evaluated_points()
bpy.ops.wm.open_mainfile(filepath=str(local_asset))
target = evaluated_points()
errors = []
if set(source) != set(target):
    errors.append(f"object-name sets differ: source-only={sorted(set(source)-set(target))[:10]}, target-only={sorted(set(target)-set(source))[:10]}")
max_delta = 0.0
max_delta_object = None
compared_vertices = 0
for name in sorted(set(source) & set(target)):
    a, b = source[name], target[name]
    if a["vertex_count"] != b["vertex_count"] or a["polygon_count"] != b["polygon_count"]:
        errors.append(f"{name}: topology count differs")
        continue
    for p0, p1 in zip(a["points"], b["points"]):
        restored = p1 + origin
        delta = max(abs(float(p0[i]-restored[i])) for i in range(3))
        compared_vertices += 1
        if delta > max_delta:
            max_delta = delta
            max_delta_object = name
if max_delta > 0.0001:
    errors.append(f"world-coordinate geometry differs by {max_delta:.9f} m at {max_delta_object}")

report = {
    "status": "PASS" if not errors else "FAIL",
    "source_graded_candidate": str(source_asset),
    "localized_asset": str(local_asset),
    "collection": collection_name,
    "placement_origin_xy_m": [float(origin.x), float(origin.y)],
    "source_geometry_object_count": len(source),
    "localized_geometry_object_count": len(target),
    "compared_evaluated_vertices": compared_vertices,
    "max_world_space_vertex_delta_m": max_delta,
    "max_delta_object": max_delta_object,
    "errors": errors,
    "method": "Evaluated vertex coordinates from the independently graded source were compared to the localized asset after restoring the master marker's XY origin; per-object vertex and polygon counts were also compared.",
}
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report))
if errors:
    raise RuntimeError("Localized asset geometry no longer matches the graded candidate")
