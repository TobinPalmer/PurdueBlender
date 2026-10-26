import bpy
import json
import math
import os

folder = os.path.dirname(__file__)
with open(os.path.join(folder, "source_feature_800_raw.json"), encoding="utf-8-sig") as f:
    feature = json.load(f)
attrs = feature["attributes"]
obj = bpy.data.objects.get("Shoemaker Cooperative")
collection = bpy.data.collections.get("Asset_massing_shoemaker_cooperative_2159ea4")
if obj is None or collection is None or obj not in collection.objects[:] or len(collection.objects) != 1:
    raise RuntimeError("Assigned object or collection structure is invalid")
ring = feature["geometry"]["rings"][0]
if ring[0] == ring[-1]:
    ring = ring[:-1]
origin_lat, origin_lon = 40.4274, -86.9137
source_points = []
for lon, lat in ring:
    p = ((lon-origin_lon)*111412.84*math.cos(math.radians(origin_lat)), (lat-origin_lat)*111040.0, 0.0)
    if p not in source_points:
        source_points.append(p)
base = [obj.matrix_world @ v.co for v in obj.data.vertices if abs((obj.matrix_world @ v.co).z) < 1e-5]
if len(source_points) != 10 or len(base) < len(source_points):
    raise RuntimeError("Could not locate every source footprint base point")
distances = [min(math.dist(p, tuple(q)) for q in base) for p in source_points]
if max(distances) > 0.001:
    raise RuntimeError(f"Source footprint differs by {max(distances):.6f} m")
coords = [obj.matrix_world @ v.co for v in obj.data.vertices]
result = {
    "opened": True,
    "asset_id": attrs["BLDG_ABBR"],
    "object": obj.name,
    "collection_objects": len(collection.objects),
    "source_ring_vertices": len(source_points),
    "max_source_ring_error_m": round(max(distances), 8),
    "mesh_vertices": len(obj.data.vertices),
    "mesh_faces": len(obj.data.polygons),
    "bounds_world_m": [[round(min(v[i] for v in coords), 6), round(max(v[i] for v in coords), 6)] for i in range(3)],
    "materials": [m.name for m in obj.data.materials],
}
with open(os.path.join(folder, "reopen_validation.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)
    f.write("\n")
print("REOPEN_VALIDATION_JSON=" + json.dumps(result))
