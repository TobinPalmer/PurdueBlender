"""Run inside Blender after opening the saved Provenance 005 library."""
import bpy
import json
import math
import os
from mathutils import Vector

asset_id = "massing_provenance_apartments_005_960f6b0"
collection_name = "Asset_" + asset_id
scene_name = "Building_" + asset_id
object_name = "Provenance Apartments.005"
root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
asset_path = os.path.join(root, "modular", "buildings", asset_id + ".blend")
source_path = os.path.join(root, "audit", asset_id, "sources", "official_purdue_fid506.json")
report_path = os.path.join(root, "audit", asset_id, "reopen_validation.json")
orthophoto_overlay = os.path.join(root, "audit", asset_id, "indiana_current_orthophoto_2025_fid506_overlay.jpg")
county_plan = os.path.join(root, "audit", asset_id, "sources", "county_provenance_phase1_2_construction_plans.pdf")
source_search = os.path.join(root, "audit", asset_id, "source_search_r3.json")

source = json.load(open(source_path, encoding="utf-8"))["feature"]
mercator_ring = source["geometry"]["rings"][0]
origin_lat, origin_lon = 40.4274, -86.9137
cos_lat = math.cos(math.radians(origin_lat))
expected = []
for x, y in mercator_ring:
    lon = math.degrees(x / 6378137.0)
    lat = math.degrees(2 * math.atan(math.exp(y / 6378137.0)) - math.pi / 2)
    expected.append(((lon-origin_lon)*111412.84*cos_lat,
                     (lat-origin_lat)*111040.0))
if expected[0] == expected[-1]:
    expected.pop()

scene = bpy.data.scenes.get(scene_name)
coll = bpy.data.collections.get(collection_name)
obj = bpy.data.objects.get(object_name)
checks = {
    "scene_exists": bool(scene),
    "asset_collection_exists": bool(coll),
    "expected_object_exists": bool(obj),
    "collection_object_count_is_one": bool(coll and len(coll.objects) == 1 and coll.objects[0] == obj),
    "object_is_mesh": bool(obj and obj.type == "MESH"),
    "no_external_images": not any(i.filepath and not i.packed_file for i in bpy.data.images),
    "orthophoto_overlay_saved": os.path.isfile(orthophoto_overlay),
    "county_construction_plan_saved": os.path.isfile(county_plan),
    "r3_exact_block_source_search_saved": os.path.isfile(source_search),
}
footprint_error = None
world_bounds = None
mesh_counts = None
if obj and obj.type == "MESH":
    mesh = obj.data
    mesh_counts = {"vertices": len(mesh.vertices), "faces": len(mesh.polygons)}
    checks["base_ring_vertex_count_matches_source"] = len(mesh.vertices) >= len(expected) and len(expected) >= 3
    errors = []
    for i, xy in enumerate(expected):
        co = obj.matrix_world @ mesh.vertices[i].co
        errors.append(math.dist((co.x, co.y), xy))
        errors.append(abs(co.z))
    footprint_error = {"max_xy_or_z_m": max(errors, default=0.0),
                       "mean_xy_or_z_m": sum(errors)/len(errors) if errors else None,
                       "source_ring_points": len(expected)}
    checks["source_ring_vertices_match_within_0_001m"] = footprint_error["max_xy_or_z_m"] <= 0.001
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    points = [evaluated.matrix_world @ Vector(corner) for corner in evaluated.bound_box]
    world_bounds = [[min(v[i] for v in points), max(v[i] for v in points)] for i in range(3)]
    checks["no_modifiers"] = len(obj.modifiers) == 0
    checks["object_has_identity_transform"] = all(abs(v) < 1e-7 for v in obj.location) and all(abs(v-1) < 1e-7 for v in obj.scale)
    checks["two_neutral_material_slots_only"] = len(mesh.materials) == 2
    checks["no_facade_projection_beyond_gis_ring"] = bool(world_bounds and world_bounds[1][0] >= min(y for _, y in expected)-0.001)
    checks["estimated_three_story_height_retained"] = bool(world_bounds and abs(world_bounds[2][1]-11.4) < 0.001)

result = {
    "status": "pass" if all(checks.values()) else "fail",
    "validation": "saved library reopened in a separate Blender process",
    "blender_version": bpy.app.version_string,
    "asset_path": os.path.relpath(asset_path, root).replace("\\", "/"),
    "scene": scene_name,
    "collection": collection_name,
    "exported_object": object_name,
    "checks": checks,
    "source_footprint_vertex_error": footprint_error,
    "evaluated_world_bounds_m": world_bounds,
    "mesh_counts": mesh_counts,
    "external_dependency_count": sum(1 for i in bpy.data.images if i.filepath and not i.packed_file),
    "note": "County plan sheet C1.4 explicitly identifies BLDG F / 143; the Purdue pre-planning FID 506 ring closely matches the current 2025 roof outline, but is not a surveyed wall registration. The exact-block search found no street-level image or approved elevation/section. The shell has no facade relief or material stationing. Project-level story count is three; eave/ridge heights and the five-break roof rhythm are estimates."
}
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)
    f.write("\n")
print("PROVENANCE_005_REOPEN_VALIDATION", json.dumps(result, sort_keys=True))
