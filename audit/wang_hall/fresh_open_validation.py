import bpy
import json
import hashlib
import math
from mathutils import Vector
from pathlib import Path

root = Path(__file__).resolve().parents[2]
asset_path = root / "modular/buildings/massing_wang_hall_wang_0dac5ab.blend"
out_path = Path(__file__).resolve().parent / "fresh_open_validation.json"
bpy.ops.wm.open_mainfile(filepath=str(asset_path))
coll = bpy.data.collections.get("Asset_massing_wang_hall_wang_0dac5ab")
scene = bpy.data.scenes.get("Building_massing_wang_hall_wang_0dac5ab")
assert coll and scene, "Expected scene or asset collection missing"
depsgraph = bpy.context.evaluated_depsgraph_get()
items = []
verts = []
object_bounds = {}
for obj in coll.objects:
    ev = obj.evaluated_get(depsgraph)
    if ev.type == "MESH":
        mesh = ev.to_mesh()
        coords = [ev.matrix_world @ v.co for v in mesh.vertices]
        verts.extend([tuple(v) for v in coords])
        if coords:
            object_bounds[obj.name] = {axis: [min(v[i] for v in coords), max(v[i] for v in coords)] for i, axis in enumerate("xyz")}
        ev.to_mesh_clear()
    items.append({
        "name": obj.name,
        "type": obj.type,
        "materials": [m.name for m in obj.data.materials if m] if getattr(obj.data, "materials", None) else [],
        "external_library": obj.library.filepath if obj.library else None,
        "modifiers": [{"name": m.name, "type": m.type} for m in obj.modifiers],
    })
assert verts, "No evaluated mesh geometry in asset collection"
bounds = {axis: [min(v[i] for v in verts), max(v[i] for v in verts)] for i, axis in enumerate("xyz")}
osm = json.loads((Path(__file__).resolve().parent / "sources" / "wang_hall_osm_way_301932787_full_2026-10-26.json").read_text(encoding="utf-8"))
way = next(e for e in osm["elements"] if e.get("type") == "way" and e.get("id") == 301932787)
nodes = {e["id"]: e for e in osm["elements"] if e.get("type") == "node"}
source_xy = [((nodes[i]["lon"] + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
              (nodes[i]["lat"] - 40.4274) * 111040.0) for i in way["nodes"]]
source_anchor = ((min(x for x, y in source_xy) + max(x for x, y in source_xy)) / 2,
                 (min(y for x, y in source_xy) + max(y for x, y in source_xy)) / 2)
source_centered_xy = [(x - source_anchor[0], y - source_anchor[1]) for x, y in source_xy]
source_bounds = {axis: [min(p[i] for p in source_centered_xy), max(p[i] for p in source_centered_xy)] for i, axis in enumerate("xy")}
structural_bounds = object_bounds.get("Wang Hall | source-backed structural footprint", {})
area2 = sum(source_centered_xy[i][0] * source_centered_xy[(i + 1) % len(source_centered_xy)][1] -
            source_centered_xy[(i + 1) % len(source_centered_xy)][0] * source_centered_xy[i][1]
            for i in range(len(source_centered_xy)))
ccw = area2 > 0
edges = []
for i, p in enumerate(source_centered_xy):
    q = source_centered_xy[(i + 1) % len(source_centered_xy)]
    dx, dy = q[0] - p[0], q[1] - p[1]
    length = math.hypot(dx, dy)
    if length < 0.8:
        continue
    tx, ty = dx / length, dy / length
    nx, ny = (ty, -tx) if ccw else (-ty, tx)
    edges.append({"p": p, "q": q, "length": length, "t": (tx, ty), "n": (nx, ny)})
front = [e for e in edges if e["length"] >= 8 and e["n"][1] < -0.25]
main = max(front, key=lambda e: e["length"])
same = [e for e in front if e["n"][0] * main["n"][0] + e["n"][1] * main["n"][1] > 0.96]
front_len = sum(e["length"] for e in same)
front_center = (sum((e["p"][0] + e["q"][0]) * 0.5 * e["length"] for e in same) / front_len,
                sum((e["p"][1] + e["q"][1]) * 0.5 * e["length"] for e in same) / front_len)
main = min(same, key=lambda e: math.hypot((e["p"][0] + e["q"][0]) * 0.5 - front_center[0],
                                          (e["p"][1] + e["q"][1]) * 0.5 - front_center[1]))
tx, ty = main["t"]
nx, ny = main["n"]
along = max(0.0, min(main["length"], (front_center[0] - main["p"][0]) * tx + (front_center[1] - main["p"][1]) * ty))
front_center = (main["p"][0] + tx * along, main["p"][1] + ty * along)
ray_origin = Vector((front_center[0] + nx * 8, front_center[1] + ny * 8, 8.38))
ray_direction = Vector((-nx, -ny, 0))
ray_hit, ray_location, ray_normal, ray_face, ray_obj, ray_matrix = scene.ray_cast(depsgraph, ray_origin, ray_direction, distance=80)
ray_first_hit_depth = ((ray_location - ray_origin).dot(ray_direction) if ray_hit else None)
result = {
    "asset": str(asset_path),
    "asset_sha256": hashlib.sha256(asset_path.read_bytes()).hexdigest(),
    "scene": scene.name,
    "collection": coll.name,
    "asset_object_count": len(items),
    "evaluated_mesh_vertex_count": len(verts),
    "evaluated_bounds_local_m": bounds,
    "object_evaluated_bounds_local_m": object_bounds,
    "structural_footprint_source_bounds_local_m": source_bounds,
    "structural_shell_evaluated_bounds_local_m": {axis: structural_bounds.get(axis) for axis in "xy"},
    "structural_footprint_bbox_delta_m": {axis: [structural_bounds[axis][i] - source_bounds[axis][i] for i in range(2)] for axis in "xy"},
    "structural_shell_height_m": structural_bounds["z"][1] - structural_bounds["z"][0],
    "atrium_front_raycast": {
        "origin_local_m": list(ray_origin),
        "direction_inward": list(ray_direction),
        "hit": ray_hit,
        "first_hit_object": ray_obj.name if ray_obj else None,
        "first_hit_depth_m": ray_first_hit_depth,
        "interpretation": "depth near 0.75m indicates front wall blocks atrium; deeper hit indicates opening at this sample"
    },
    "width_m": bounds["x"][1] - bounds["x"][0],
    "depth_m": bounds["y"][1] - bounds["y"][0],
    "height_m": bounds["z"][1] - bounds["z"][0],
    "external_libraries": [item for item in items if item["external_library"]],
    "images": [{"name": img.name, "filepath": img.filepath, "packed": bool(img.packed_file)} for img in bpy.data.images],
    "objects": items,
    "checks": {
        "fresh_open": True,
        "expected_scene_and_collection": True,
        "evaluated_geometry_nonempty": True,
        "local_asset_anchor_expected_xy": [98.2954902278031, 339.9100960000692],
        "structural_outline_source_matched": all(abs(structural_bounds[a][i] - source_bounds[a][i]) < 0.001 for a in "xy" for i in range(2)),
        "atrium_wall_cut_at_sample": bool(ray_hit and ray_first_hit_depth and ray_first_hit_depth > 1.5),
        "estimated_structural_shell_height_m": structural_bounds["z"][1] - structural_bounds["z"][0],
        "placement_marker_in_asset_library": False,
        "placement_status": "local asset; coordinator must integrate with a detailed Placement marker at the recorded campus anchor",
        "external_library_dependencies": "none_expected"
    }
}
out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
print("WANG_FRESH_OPEN_OK", json.dumps({k: result[k] for k in ["asset_sha256", "asset_object_count", "evaluated_mesh_vertex_count", "evaluated_bounds_local_m", "width_m", "depth_m", "height_m", "external_libraries"]}))
