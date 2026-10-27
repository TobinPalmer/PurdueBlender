"""Reopen and audit the Horticulture Building asset with Blender 5.2.3."""
import bpy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET_PATH = ROOT / "modular" / "buildings" / "horticulture_building.blend"
OUT = Path(__file__).resolve().parent / "reopen_validation.json"
MANIFEST_PATH = ROOT / "modular" / "manifest.json"
GIS_PATH = Path(__file__).resolve().parent / "sources" / "purdue_gis_fid232.json"

bpy.ops.wm.open_mainfile(filepath=str(ASSET_PATH))
with MANIFEST_PATH.open(encoding="utf-8") as f:
    manifest = json.load(f)
record = next(item for item in manifest["assets"] if item["id"] == "horticulture_building")
with GIS_PATH.open(encoding="utf-8") as f:
    gis = json.load(f)
asset = bpy.data.collections.get("Asset_horticulture_building")
assert asset is not None, "expected export collection missing after reopen"
assert asset.get("building_id") == "horticulture_building"
assert asset.get("source_feature_id") == 232
assert asset.get("local_coordinates") is True
assert all(abs(a - b) < 1e-8 for a, b in zip(asset.get("placement_origin_xy_m"), record["placement_origin_xy_m"]))
assert all(abs(a - b) < 1e-8 for a, b in zip(asset.get("placement_origin_xy_m"), [-61.82494487966297, -630.9233289999372]))

shell = bpy.data.objects.get("HORT structural shell | official GIS FID 232 outline")
assert shell is not None and shell.type == "MESH"
shell_eval = shell.evaluated_get(bpy.context.evaluated_depsgraph_get())
mesh = shell_eval.to_mesh()
try:
    verts = [tuple(shell_eval.matrix_world @ v.co) for v in mesh.vertices]
finally:
    shell_eval.to_mesh_clear()
mins = [min(v[i] for v in verts) for i in range(3)]
maxs = [max(v[i] for v in verts) for i in range(3)]
assert 10.68 <= maxs[2] <= 10.72
assert mins[2] == 0.0
assert maxs[0] - mins[0] > 60 and maxs[1] - mins[1] > 40
assert len(asset.all_objects) > 20
assert abs(asset.get("height_range_m")[0] - maxs[2]) < 0.01
assert 14.62 <= asset.get("height_range_m")[1] <= 14.64
assert "feet" in asset.get("height_status", "") and "does not publish" in asset.get("height_status", "")
assert "west-facing" in asset.get("photo_elevation", "")
assert not any("canopy" in obj.name.lower() or "portico pier" in obj.name.lower() for obj in asset.all_objects)

bad_paths = []
for image in bpy.data.images:
    if image.source == "FILE" and image.filepath and not image.filepath.startswith("//"):
        bad_paths.append(image.filepath)
assert not bad_paths, f"non-portable external image paths: {bad_paths}"

material_links = {}
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    links = list(mat.node_tree.links)
    surface_connected = any(link.to_node.type == "OUTPUT_MATERIAL" and link.to_socket.name == "Surface" for link in links)
    material_links[mat.name] = surface_connected
assert material_links and all(material_links.values())

# The structural shell is an exact extrusion of the locally projected GIS
# outline. These points use the same documented local-frame transform.
lat0, lon0 = 40.4274, -86.9137
lon_m = 111412.84 * math.cos(math.radians(lat0))
lat_m = 111040.0
geo = gis["geometry"]["rings"][0]
if geo[0] == geo[-1]:
    geo = geo[:-1]
projected = [((p[0] - lon0) * lon_m, (p[1] - lat0) * lat_m) for p in geo]
origin = record["placement_origin_xy_m"]
local = [(p[0] - origin[0], p[1] - origin[1]) for p in projected]
mesh_footprint = sorted(set((round(v[0], 5), round(v[1], 5)) for v in verts if abs(v[2]) < 1e-5))
source_footprint = sorted(set((round(p[0], 5), round(p[1], 5)) for p in local))
footprint_vertex_count_source = len(source_footprint)
footprint_vertex_count_mesh = len(mesh_footprint)
source_to_mesh = max(min(math.dist(p, q) for q in mesh_footprint) for p in source_footprint)
mesh_to_source = max(min(math.dist(p, q) for q in source_footprint) for p in mesh_footprint)
assert source_to_mesh <= 0.25 and mesh_to_source <= 0.25

sha = hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()
result = {
    "asset_file": "modular/buildings/horticulture_building.blend",
    "saved_and_reopened": True,
    "blender_version": bpy.app.version_string,
    "asset_id": asset.get("building_id"),
    "collection": asset.name,
    "source_feature_id": asset.get("source_feature_id"),
    "placement_origin_xy_m": list(asset.get("placement_origin_xy_m")),
    "collection_local_bounds_m": [[mins[0], maxs[0]], [mins[1], maxs[1]], [mins[2], maxs[2]]],
    "shell_source_gis_vertex_count": len(local),
    "shell_mesh_floor_vertex_count": footprint_vertex_count_mesh,
    "source_unique_vertex_count_unsimplified": footprint_vertex_count_source,
    "max_source_to_shell_vertex_error_m": source_to_mesh,
    "max_shell_to_source_vertex_error_m": mesh_to_source,
    "shell_object_count": len(asset.all_objects),
    "asset_children": [c.name for c in asset.children],
    "nonportable_image_paths": bad_paths,
    "material_surface_links": material_links,
    "height_m": asset.get("height_m"),
    "height_status": asset.get("height_status"),
    "height_range_m": list(asset.get("height_range_m")),
    "photo_elevation": asset.get("photo_elevation"),
    "sha256": sha,
    "limits": [
        "GIS service gives no survey tolerance or source date; the 0.25 m simplification and approximate local conversion add uncertainty.",
        "Height is an estimate: GIS vertical attributes conflict with the three window levels in the Purdue exterior photograph.",
        "Facade spacing and entry dimensions are estimated from the single exterior photograph; no measured elevations were available.",
    ],
}
OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2), flush=True)
