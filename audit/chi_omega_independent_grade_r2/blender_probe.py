"""Fresh-process read-only probe for the Chi Omega candidate."""
import bpy, json, math, sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
grade = root / "audit" / "chi_omega_independent_grade_r2"
asset = root / "modular" / "buildings" / "massing_chi_omega_a9eb08d.blend"
source = root / "audit" / "chi_omega" / "sources" / "purdue_gis_fid781_chi_omega_2026-10-26.json"
output = grade / "blender_probe.json"
log = grade / "blender_probe.log"
origin_lat, origin_lon = 40.4274, -86.9137

def emit(message):
    with log.open("a", encoding="utf-8") as f:
        f.write(message + "\n")
    print(message)

log.write_text("Chi Omega independent Blender 4.5.15 probe\n", encoding="utf-8")
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene = bpy.data.scenes.get("Building_massing_chi_omega_a9eb08d")
coll = bpy.data.collections.get("Asset_massing_chi_omega_a9eb08d")
assert scene is not None and coll is not None
objects = list(coll.objects)
meshes = [obj for obj in objects if obj.type == "MESH"]
assert len(objects) == len(meshes) == 1
obj = meshes[0]
assert obj.name == "Chi Omega" and obj.get("building_id") == "massing_chi_omega_a9eb08d"
assert len(obj.modifiers) == 0
assert all(abs(obj.matrix_world[i][j] - (1 if i == j else 0)) < 1e-6 for i in range(4) for j in range(4))
coords = [obj.matrix_world @ v.co for v in obj.data.vertices]
bounds = [[min(p[i] for p in coords), max(p[i] for p in coords)] for i in range(3)]
record = json.loads(source.read_text(encoding="utf-8"))["features"][0]
attrs, ring = record["attributes"], record["geometry"]["rings"][0][:-1]
expected = {(round((lon-origin_lon)*111412.84*math.cos(math.radians(origin_lat)), 4), round((lat-origin_lat)*111040.0, 4)) for lon, lat in ring}
actual = {(round(p.x, 4), round(p.y, 4)) for p in coords if abs(p.z) < 1e-6}
distances = [min(math.hypot(x-ax, y-ay) for ax, ay in actual) for x, y in expected]
footprint_ok = len(actual) == len(expected) and max(distances, default=1e9) <= 0.02
assert footprint_ok
assert attrs["FID"] == 781 and attrs["BUILDING_N"] == "Chi Omega"
assert attrs["ADDRESS"] == "402 Waldron St"
result = {
    "blender_version": bpy.app.version_string,
    "asset_path": str(asset.relative_to(root)),
    "asset_sha256": None,
    "scene": scene.name,
    "collection": coll.name,
    "object_count": len(objects),
    "mesh_count": len(meshes),
    "mesh_name": obj.name,
    "building_id": obj.get("building_id"),
    "source_feature_id": attrs["FID"],
    "source_name": attrs["BUILDING_N"],
    "source_address": attrs["ADDRESS"],
    "gis_crs": record["geometry"].get("spatialReference", {}).get("wkid", 4326),
    "footprint_vertex_count": len(expected),
    "candidate_ground_vertex_count": len(actual),
    "max_gis_ground_ring_error_m": max(distances, default=None),
    "footprint_matches_transformed_gis_within_0_02m": footprint_ok,
    "evaluated_world_bounds_m": bounds,
    "object_transform_identity": True,
    "modifier_count": len(obj.modifiers),
    "linked_library_count": len(bpy.data.libraries),
    "material_names": [m.name for m in obj.data.materials],
    "fresh_process_reopen": True,
}
output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
emit(json.dumps(result, indent=2))
