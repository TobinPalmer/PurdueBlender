"""Read-only independent reopen probe for the saved Circle K library."""
import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ID = "massing_circle_k_fa39c23"
ASSET = ROOT / "modular" / "buildings" / (ID + ".blend")
EVIDENCE = ROOT / "audit" / "circle_k"
OUT = ROOT / "audit" / "circle_k_independent_grade" / "blender_probe.json"
MANIFEST = json.loads((ROOT / "modular" / "manifest.json").read_text(encoding="utf-8"))
manifest_item = next(x for x in MANIFEST["assets"] if x["id"] == ID)
scene_name = "Building_" + ID
collection_name = "Asset_" + ID
scene = bpy.data.scenes.get(scene_name)
collection = bpy.data.collections.get(collection_name)
assert scene and collection and collection in list(scene.collection.children)
assert bpy.context.scene == scene

element_data = json.loads((EVIDENCE / "sources" / "osm_way_345144282_full_2026-10-26.json").read_text(encoding="utf-8"))
way = next(e for e in element_data["elements"] if e["type"] == "way" and e["id"] == 345144282)
nodes = {e["id"]: e for e in element_data["elements"] if e["type"] == "node"}
origin_lat, origin_lon = 40.4274, -86.9137
lon_m = 111412.84 * math.cos(math.radians(origin_lat))
lat_m = 111040.0
source = []
for node_id in way["nodes"][:-1]:
    n = nodes[node_id]
    source.append(((n["lon"] - origin_lon) * lon_m, (n["lat"] - origin_lat) * lat_m))

shell = bpy.data.objects.get("Circle K")
assert shell is not None and shell.type == "MESH"
actual = [(float(v.co.x), float(v.co.y)) for v in shell.data.vertices]
def nearest(a, points):
    return min(math.hypot(a[0]-b[0], a[1]-b[1]) for b in points)
hausdorff = max(max(nearest(p, actual) for p in source), max(nearest(p, source) for p in actual))
def bounds(points):
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(2)]
sb, ab = bounds(source), bounds(actual)
source_center = [(v[0]+v[1])/2 for v in sb]
actual_center = [(v[0]+v[1])/2 for v in ab]

depsgraph = bpy.context.evaluated_depsgraph_get()
entries = []
all_world = []
for obj in collection.objects:
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    nverts = len(mesh.vertices) if mesh else 0
    if mesh:
        evaluated.to_mesh_clear()
    corners = [evaluated.matrix_world @ Vector(c) for c in evaluated.bound_box]
    all_world.extend(corners)
    entries.append({"name": obj.name, "type": obj.type, "evaluated_vertices": nverts,
                    "dimensions_m": [round(float(x), 5) for x in obj.dimensions],
                    "modifiers": [m.name for m in obj.modifiers],
                    "library": obj.library.filepath if obj.library else None})
world_bounds = [[min(float(p[i]) for p in all_world), max(float(p[i]) for p in all_world)] for i in range(3)]
external = []
for image in bpy.data.images:
    if image.source == "FILE" and image.filepath and not image.packed_file:
        external.append(image.filepath)
libraries = [lib.filepath for lib in bpy.data.libraries]
result = {
    "probe_version": 1,
    "asset_path": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
    "asset_sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
    "blender_version": bpy.app.version_string,
    "scene": scene.name,
    "collection": collection.name,
    "collection_is_direct_scene_child": collection in list(scene.collection.children),
    "collection_object_count": len(collection.objects),
    "object_types": {kind: sum(1 for o in collection.objects if o.type == kind) for kind in sorted({o.type for o in collection.objects})},
    "object_names": sorted(o.name for o in collection.objects),
    "world_bounds_m": world_bounds,
    "store_shell_dimensions_m": [float(x) for x in shell.dimensions],
    "store_shell_bounds_xy_m": ab,
    "store_shell_center_xy_m": actual_center,
    "source_way_id": way["id"],
    "source_tags": way.get("tags", {}),
    "source_vertices_local_m": source,
    "source_bounds_xy_m": sb,
    "source_center_xy_m": source_center,
    "symmetric_hausdorff_xy_error_m": hausdorff,
    "manifest_expected_object_count": manifest_item.get("object_count"),
    "manifest_expected_object_names": manifest_item.get("objects"),
    "external_unpacked_images": external,
    "linked_library_paths": libraries,
    "objects": entries,
    "all_evaluated_geometry_nonempty": all(e["evaluated_vertices"] > 0 for e in entries),
    "zero_modifiers": all(not e["modifiers"] for e in entries),
}
OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print("CIRCLE_K_INDEPENDENT_PROBE " + json.dumps({k: result[k] for k in (
    "asset_sha256", "blender_version", "collection_object_count", "world_bounds_m",
    "store_shell_dimensions_m", "symmetric_hausdorff_xy_error_m", "manifest_expected_object_count",
    "external_unpacked_images", "linked_library_paths")}, sort_keys=True))
