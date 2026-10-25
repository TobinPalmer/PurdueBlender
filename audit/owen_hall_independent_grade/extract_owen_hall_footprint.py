"""Blender-side extractor used by validate_owen_hall_footprint.py."""
import bpy
import json
import sys
from collections import Counter
from pathlib import Path

blend, out = sys.argv[-2:]
bpy.ops.wm.open_mainfile(filepath=blend)
col = bpy.data.collections.get("Asset_owen_hall")
obj = bpy.data.objects.get("Owen_GIS_Limestone_Base")
root = bpy.data.objects.get("AssetRoot_owen_hall")
if col is None or obj is None or root is None:
    raise RuntimeError("Expected Owen asset collection, GIS base shell, or local root is missing")
depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated = obj.evaluated_get(depsgraph)
mesh = evaluated.to_mesh()
bottom_edge_uses = {}
for face in mesh.polygons:
    if not all(abs(mesh.vertices[idx].co.z) < 1e-7 for idx in face.vertices):
        continue
    for key in face.edge_keys:
        key = tuple(sorted(key))
        bottom_edge_uses[key] = bottom_edge_uses.get(key, 0) + 1
boundary = {}
for (a, b), uses in bottom_edge_uses.items():
    if uses != 1:
        continue
    boundary.setdefault(a, []).append(b)
    boundary.setdefault(b, []).append(a)
if not boundary or any(len(nbrs) != 2 for nbrs in boundary.values()):
    raise RuntimeError("Could not recover a single closed base outline from the evaluated mesh")
start = min(boundary)
ordered_ids = [start]
previous, current = None, start
while True:
    next_id = next(idx for idx in boundary[current] if idx != previous)
    if next_id == start:
        break
    if next_id in ordered_ids:
        raise RuntimeError("Footprint boundary repeats before closing")
    ordered_ids.append(next_id)
    previous, current = current, next_id
xy = [((obj.matrix_world @ mesh.vertices[idx].co).x,
       (obj.matrix_world @ mesh.vertices[idx].co).y) for idx in ordered_ids]
evaluated.to_mesh_clear()
all_mesh_points = []
depsgraph = bpy.context.evaluated_depsgraph_get()
for other in col.objects:
    if other.type != "MESH":
        continue
    evaluated_other = other.evaluated_get(depsgraph)
    other_mesh = evaluated_other.to_mesh()
    for vertex in other_mesh.vertices:
        p = other.matrix_world @ vertex.co
        all_mesh_points.append((p.x, p.y, p.z))
    evaluated_other.to_mesh_clear()
image_or_library_refs = []
for image in bpy.data.images:
    if image.source == "FILE":
        image_or_library_refs.append({"name": image.name, "filepath": image.filepath, "packed": image.packed_file is not None})
for library in bpy.data.libraries:
    image_or_library_refs.append({"library": library.filepath})
def dims(name):
    item = bpy.data.objects.get(name)
    return list(item.dimensions) if item else None
record = {
    "blend_path": blend,
    "scene_names": [s.name for s in bpy.data.scenes],
    "collection_name": col.name,
    "collection_object_count": len(col.objects),
    "object_type_counts": dict(Counter(o.type for o in col.objects)),
    "local_root_translation_m": list(root.matrix_world.translation),
    "evaluated_collection_mesh_bounds_local_m": [[min(p[i] for p in all_mesh_points), max(p[i] for p in all_mesh_points)] for i in range(3)],
    "mesh_modifier_count": sum(bool(o.modifiers) for o in col.objects if o.type == "MESH"),
    "external_image_or_library_references": image_or_library_refs,
    "node_material_count": sum(m.use_nodes for m in bpy.data.materials),
    "external_facade_window_count": sum(o.name.startswith(("Owen_Win_East_", "Owen_Win_West_", "Owen_Win_North_", "Owen_Win_South_")) for o in col.objects),
    "facade_frame_assembly_vertices": len(bpy.data.objects["Owen_R2_WindowFrames_All"].data.vertices),
    "facade_louver_assembly_vertices": len(bpy.data.objects["Owen_R2_WindowLouvers_All"].data.vertices),
    "room_vignette_dimensions_m": {
        "floor": dims("Owen_Dorm_StandardRoom_Floor"),
        "north_south_walls": dims("Owen_Dorm_StandardRoom_Wall_N"),
        "east_wall": dims("Owen_Dorm_StandardRoom_Wall_E"),
        "closet": dims("Owen_Dorm_Wardrobes"),
        "standard_mattress_0": dims("Owen_Dorm_Bed_Mattress_0"),
    },
    "illustrative_standard_double_module_count": 1 + len({tuple(o.name.split("_")[3:5]) for o in col.objects if o.name.startswith("Owen_R2_StandardDouble_F")}),
    "duplicated_room_module_object_count": sum(o.name.startswith("Owen_R2_StandardDouble_") for o in col.objects),
    "room_amenity_objects": [o.name for o in col.objects if o.name.startswith("Owen_R2_StandardRoom_") or o.name.startswith("Owen_R2_Room_")],
    "footprint_object": obj.name,
    "footprint_vertex_xy_local_m": xy,
    "footprint_mesh_vertices": len(obj.data.vertices),
    "footprint_mesh_faces": len(obj.data.polygons),
    "material_names": [m.name for m in obj.data.materials],
    "modifier_count": len(obj.modifiers),
}
Path(out).write_text(json.dumps(record, indent=2), encoding="utf-8")
print(json.dumps({k: v for k, v in record.items() if k != "footprint_vertex_xy_local_m"}, indent=2))
