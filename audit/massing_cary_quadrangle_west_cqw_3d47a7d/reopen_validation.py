"""Reopen-and-inspect CQW's saved Blender library; run with Blender Python."""
import bpy
import bmesh
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_cary_quadrangle_west_cqw_3d47a7d"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
OUT = ROOT / "audit" / ASSET_ID / "reopen_validation.json"
COLLECTION = f"Asset_{ASSET_ID}"
SCENE = f"Building_{ASSET_ID}"

if bpy.context.scene.name != SCENE:
    raise RuntimeError(f"Expected {SCENE}, got {bpy.context.scene.name}")
coll = bpy.data.collections.get(COLLECTION)
if coll is None:
    raise RuntimeError(f"Missing exported collection {COLLECTION}")
objects = list(coll.objects)
mesh_objects = [obj for obj in objects if obj.type == "MESH"]
if not mesh_objects:
    raise RuntimeError("Exported collection has no mesh geometry")

# Evaluate object bounds after Blender modifiers, while avoiding copies of the
# full mesh for every repeated window and stone trim element.
depsgraph = bpy.context.evaluated_depsgraph_get()
coords = []
modifier_counts = {}
for obj in objects:
    for mod in obj.modifiers:
        modifier_counts[mod.type] = modifier_counts.get(mod.type, 0) + 1
    if obj.type != "MESH":
        continue
    ev = obj.evaluated_get(depsgraph)
    for corner in ev.bound_box:
        coords.append(ev.matrix_world @ Vector(corner))
if not coords:
    raise RuntimeError("No evaluated mesh bounds found")
bounds = [[min(p[i] for p in coords), max(p[i] for p in coords)] for i in range(3)]

shell = bpy.data.objects.get("Cary Quadrangle West (CQW) shell")
if shell is None or shell.name not in coll.objects:
    raise RuntimeError("Expected source-footprint shell is missing")
bm = bmesh.new()
bm.from_mesh(shell.data)
nonmanifold_shell_edges = sum(not edge.is_manifold for edge in bm.edges)
boundary_shell_edges = sum(edge.is_boundary for edge in bm.edges)
bm.free()

source_path = ROOT / "audit" / ASSET_ID / "sources" / "purdue_cqw_fid60_wgs84.geojson"
src = json.loads(source_path.read_text(encoding="utf-8"))["features"][0]
ring = src["geometry"]["coordinates"][0]
xy = []
for lon, lat in ring:
    x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
    y = (lat - 40.4274) * 111040.0
    xy.append((x, y))
if xy and xy[0] == xy[-1]:
    xy.pop()
source_bounds = [[min(p[i] for p in xy), max(p[i] for p in xy)] for i in range(2)]
source_area = abs(sum(xy[i][0] * xy[(i + 1) % len(xy)][1] -
                      xy[(i + 1) % len(xy)][0] * xy[i][1]
                      for i in range(len(xy))) / 2)

record = {
    "asset_id": ASSET_ID,
    "asset_file": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
    "reopened_in_blender": bpy.app.version_string,
    "scene": bpy.context.scene.name,
    "collection": COLLECTION,
    "collection_object_count": len(objects),
    "mesh_object_count": len(mesh_objects),
    "modifier_counts": modifier_counts,
    "evaluated_world_bounds_m": bounds,
    "source_gis": {
        "feature_id": src["properties"]["FID"],
        "building_abbreviation": src["properties"]["BLDG_ABBR"],
        "official_levels": src["properties"]["NUM_LEVELS"],
        "official_extrusion_attribute": src["properties"]["Extrution"],
        "source_ring_vertex_count": len(ring),
        "projected_ring_vertex_count": len(xy),
        "projected_bounds_m": source_bounds,
        "projected_area_m2": source_area,
        "source_crs": "EPSG:3857 transformed to WGS84, then repository local approximate campus coordinates",
    },
    "shell_topology": {
        "nonmanifold_edge_count": nonmanifold_shell_edges,
        "boundary_edge_count": boundary_shell_edges,
    },
    "rendered_previews": [
        "audit/massing_cary_quadrangle_west_cqw_3d47a7d/preview_cqw_east_court.png",
        "audit/massing_cary_quadrangle_west_cqw_3d47a7d/preview_cqw_entrance.png",
    ],
    "asset_transform": "Campus-coordinate massing; mesh data and object placements carry the source GIS local projection; no master edit or placement marker change.",
    "remaining_uncertainty": [
        "Purdue ArcGIS does not define the units of Extrution=48; body height 14.63 m assumes feet.",
        "Tower height, exact floor-to-floor heights, roof construction, window count, and facade dimensions are estimates from historic exterior photos.",
        "The exported source polygon is authoritative for plan outline; GIS survey tolerance and wall-vs-overhang relationship are unavailable.",
    ],
}
OUT.write_text(json.dumps(record, indent=2), encoding="utf-8")
print(json.dumps(record, indent=2))
