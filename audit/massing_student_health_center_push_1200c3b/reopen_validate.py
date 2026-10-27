"""Reopen and validate the PUSH library with Blender's evaluated mesh."""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_student_health_center_push_1200c3b"
COLLECTION_NAME = "Asset_" + ASSET_ID
OUT = Path(__file__).with_name("reopen_verification.json")

coll = bpy.data.collections.get(COLLECTION_NAME)
assert coll is not None, f"Missing exported collection {COLLECTION_NAME}"
assert len(coll.objects) == 1, f"Expected 1 asset object, found {len(coll.objects)}"
obj = coll.objects[0]
assert obj.type == "MESH", f"Expected mesh, found {obj.type}"
assert obj.name == "Student Health Center (PUSH)"
depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated = obj.evaluated_get(depsgraph)
mesh = evaluated.to_mesh()
try:
    coords = [evaluated.matrix_world @ v.co for v in mesh.vertices]
    eval_vertex_count = len(mesh.vertices)
    eval_polygon_count = len(mesh.polygons)
finally:
    evaluated.to_mesh_clear()
bounds = [
    [min(v[i] for v in coords), max(v[i] for v in coords)]
    for i in range(3)
]
expected = [[-229.04404, -172.68895], [294.14559, 364.79266], [0.0, 14.6304]]
errors = [
    abs(bounds[axis][side] - expected[axis][side])
    for axis in range(3)
    for side in range(2)
]
assert max(errors[:4]) < 0.25, f"XY placement/bounds mismatch: {bounds}"
assert abs(bounds[2][0]) < 0.02, f"Unexpected below-grade geometry: {bounds[2]}"
assert abs(bounds[2][1] - 14.6304) < 0.02, f"Height mismatch: {bounds[2]}"
assert eval_polygon_count > 500, f"Unexpectedly low polygon count {eval_polygon_count}"
assert len(obj.data.materials) >= 5
external_images = [
    image.filepath for image in bpy.data.images
    if image.source == "FILE" and image.filepath and not image.packed_file
]
report = {
    "asset_id": ASSET_ID,
    "blend_reopened": True,
    "scene": bpy.context.scene.name,
    "collection": coll.name,
    "collection_object_count": len(coll.objects),
    "object": obj.name,
    "object_type": obj.type,
    "evaluated_vertex_count": eval_vertex_count,
    "evaluated_polygon_count": eval_polygon_count,
    "material_count": len(obj.data.materials),
    "evaluated_bounds_world_m": bounds,
    "max_xy_bound_error_m": max(errors[:4]),
    "evaluated_height_m": bounds[2][1] - bounds[2][0],
    "minimum_elevation_m": bounds[2][0],
    "modifiers": [{"name": m.name, "type": m.type, "show_render": m.show_render} for m in obj.modifiers],
    "unpacked_external_images": external_images,
    "result": "pass" if not external_images else "review external image dependencies",
}
OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print("PUSH_REOPEN_VERIFICATION=" + json.dumps(report))
