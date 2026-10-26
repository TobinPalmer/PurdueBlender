"""Reopen the exported asset in Blender and write an independent geometry check."""
import bpy, json, math, os

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
out = os.path.join(os.path.dirname(__file__), "reopen_validation.json")
expected_scene = "Building_massing_purdue_police_department_19f467e"
expected_collection = "Asset_massing_purdue_police_department_19f467e"
expected_object = "Purdue Police Department"
scene = bpy.data.scenes.get(expected_scene)
collection = bpy.data.collections.get(expected_collection)
obj = bpy.data.objects.get(expected_object)
assert scene is not None, "manifest scene not found"
assert collection is not None, "manifest collection not found"
assert obj is not None and obj.type == "MESH", "expected exported mesh object not found"
assert obj.name in collection.objects, "asset mesh not in expected collection"
assert len(collection.objects) == 1, "export collection must contain exactly one object"
assert tuple(round(x, 6) for x in obj.location) == (0.0, 0.0, 0.0)
assert tuple(round(x, 6) for x in obj.rotation_euler) == (0.0, 0.0, 0.0)
assert tuple(round(x, 6) for x in obj.scale) == (1.0, 1.0, 1.0)

world = [obj.matrix_world @ v.co for v in obj.data.vertices]
bounds = [[min(v[i] for v in world), max(v[i] for v in world)] for i in range(3)]
bottom_points = {(round(v.x, 3), round(v.y, 3)) for v in world if abs(v.z) < 1e-5}
gis_path = os.path.join(root, "audit", "massing_purdue_police_department_19f467e", "sources", "purdue_gis_fid_275.json")
with open(gis_path, encoding="utf-8") as f:
    feature = next(x for x in json.load(f)["features"] if x["attributes"]["FID"] == 275)
ring = feature["geometry"]["rings"][0]
R = 6378137.0
foot = []
for x, y in ring:
    lon = math.degrees(x / R)
    lat = math.degrees(2.0 * math.atan(math.exp(y / R)) - math.pi / 2.0)
    foot.append(((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
                 (lat - 40.4274) * 111040.0))
if len(foot) > 1 and math.dist(foot[0], foot[-1]) < 0.001:
    foot.pop()
foot_rounded = [(round(x, 3), round(y, 3)) for x, y in foot]
perimeter = sum(math.dist(foot[i], foot[(i+1) % len(foot)]) for i in range(len(foot)))
area = abs(sum(foot[i][0]*foot[(i+1) % len(foot)][1] - foot[(i+1) % len(foot)][0]*foot[i][1]
               for i in range(len(foot))) / 2.0)
max_footprint_vertex_error = max(min(math.dist(p, q) for q in bottom_points) for p in foot_rounded)
footprint_bounds = [[min(p[0] for p in foot), max(p[0] for p in foot)],
                    [min(p[1] for p in foot), max(p[1] for p in foot)]]
mods = [{"name": m.name, "type": m.type} for m in obj.modifiers]
materials = sorted({m.name for m in obj.data.materials if m})
record = {
    "opened_blend": bpy.data.filepath,
    "scene": scene.name,
    "expected_collection": collection.name,
    "collection_object_names": sorted(o.name for o in collection.objects),
    "object": obj.name,
    "object_type": obj.type,
    "vertices": len(obj.data.vertices),
    "polygons": len(obj.data.polygons),
    "bounds_world_m": bounds,
    "bottom_footprint_unique_vertices": len(bottom_points),
    "source_footprint_vertices": len(foot),
    "source_footprint_bounds_campus_xy_m": footprint_bounds,
    "source_footprint_area_m2_project_approx": area,
    "source_footprint_perimeter_m_project_approx": perimeter,
    "max_source_to_mesh_bottom_vertex_error_m": max_footprint_vertex_error,
    "transform": {"location": list(obj.location), "rotation_euler": list(obj.rotation_euler), "scale": list(obj.scale)},
    "modifiers": mods,
    "materials": materials,
    "packed_image_count": sum(1 for i in bpy.data.images if i.packed_file),
    "external_unpacked_image_paths": [i.filepath for i in bpy.data.images if i.source == "FILE" and not i.packed_file],
    "checks": {
        "manifest_scene_collection_object_and_count": True,
        "campus_world_coordinates_preserved": True,
        "asset_reopens_in_blender": True,
        "no_unpacked_image_dependencies": not any(i.source == "FILE" and not i.packed_file for i in bpy.data.images),
        "modifier_stack_recorded": True,
        "footprint_remeasured_from_mesh": True,
        "mesh_bottom_vertices_match_official_gis_ring_within_2mm": max_footprint_vertex_error < 0.002,
    },
}
with open(out, "w", encoding="utf-8") as f:
    json.dump(record, f, indent=2)
    f.write("\n")
print("VALIDATION", json.dumps(record, sort_keys=True))
