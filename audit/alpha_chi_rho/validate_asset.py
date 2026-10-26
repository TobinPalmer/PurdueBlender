"""Read-only validation for the saved Alpha Chi Rho Blender library."""

import json
import math
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "audit" / "alpha_chi_rho" / "sources" / "purdue_gis_FID775_alpha_chi_rho_2026-10-26.json"
OUTPUT = ROOT / "audit" / "alpha_chi_rho" / "reopen_validation.json"
ASSET_ID = "massing_alpha_chi_rho_0cb591a"
COLLECTION = "Asset_massing_alpha_chi_rho_0cb591a"
ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
WALL_HEIGHT = 6.2


def local_xy(lon, lat):
    return ((lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT)),
            (lat - ORIGIN_LAT) * 111040.0)


def polygon_area(points):
    return 0.5 * sum(points[i][0] * points[(i + 1) % len(points)][1]
                     - points[(i + 1) % len(points)][0] * points[i][1]
                     for i in range(len(points)))


data = json.loads(SOURCE.read_text(encoding="utf-8"))
feature = data["features"][0]
assert feature["attributes"]["FID"] == 775
ring = feature["geometry"]["rings"][0]
gis_xy = [local_xy(lon, lat) for lon, lat in ring[:-1]]
col = bpy.data.collections.get(COLLECTION)
assert col is not None, f"Missing exported collection {COLLECTION}"
objects = list(col.objects)
assert len(objects) == 1, f"Expected one building object, got {len(objects)}"
obj = objects[0]
assert obj.name == "Alpha Chi Rho" and obj.type == "MESH"

# The primary shell has material slot 0. Pull its wall-base vertices and
# compare their footprint vertices directly with the official GIS ring.
mesh = obj.data
shell_vertices = set()
for poly in mesh.polygons:
    if poly.material_index != 0:
        continue
    for vid in poly.vertices:
        co = mesh.vertices[vid].co
        if abs(co.z) < 1e-5 or abs(co.z - WALL_HEIGHT) < 1e-5:
            shell_vertices.add((round(co.x, 5), round(co.y, 5)))
assert len(shell_vertices) == len(gis_xy), (len(shell_vertices), len(gis_xy))
vertex_errors = [min(math.hypot(x - gx, y - gy) for gx, gy in gis_xy)
                 for x, y in shell_vertices]
assert max(vertex_errors) <= 0.001, max(vertex_errors)

scene = bpy.context.scene
asset_scene_names = [s.name for s in bpy.data.scenes]
assert "Building_massing_alpha_chi_rho_0cb591a" in asset_scene_names
assert bpy.context.scene.name == "Building_massing_alpha_chi_rho_0cb591a"
all_vertices = [obj.matrix_world @ v.co for v in mesh.vertices]
bounds = [[min(v[i] for v in all_vertices), max(v[i] for v in all_vertices)] for i in range(3)]
gis_bounds = [[min(p[i] for p in gis_xy), max(p[i] for p in gis_xy)] for i in (0, 1)]
image_paths = [im.filepath for im in bpy.data.images if im.source == "FILE" and im.filepath]
result = {
    "status": "PASS",
    "reopened_file": bpy.data.filepath,
    "scene": scene.name,
    "expected_collection": COLLECTION,
    "collection_object_count": len(objects),
    "object_name": obj.name,
    "mesh_vertices": len(mesh.vertices),
    "mesh_polygons": len(mesh.polygons),
    "material_count": len(mesh.materials),
    "external_image_paths": image_paths,
    "gis_feature_id": 775,
    "gis_ring_vertices": len(gis_xy),
    "shell_footprint_vertex_match": True,
    "shell_footprint_max_vertex_error_m": max(vertex_errors),
    "gis_xy_bounds_m": gis_bounds,
    "gis_xy_area_m2_project_approx": abs(polygon_area(gis_xy)),
    "whole_object_bounds_m_including_facade_and_porch_details": bounds,
    "estimated_wall_height_m": WALL_HEIGHT,
    "height_status": "estimated from two visible stories in an undated street panorama; no measured elevation located",
    "facade_basis": "Google Street View pano VCE1Wee15-lqG_KbYR239Q; retrieved 2026-10-26, capture date not exposed",
    "footprint_cross_check": "Indiana 2018 LiDAR-derived footprint comparison; broad agreement, measurable boundary discrepancy recorded separately",
    "external_file_dependencies": image_paths,
}
OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
