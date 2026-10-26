import bpy
import json
import math
import os

folder = os.path.dirname(__file__)
with open(os.path.join(folder, "source_feature_258_raw.json"), encoding="utf-8-sig") as f:
    feature = json.load(f)
attrs = feature["attributes"]
obj = bpy.data.objects.get("Shreve Hall")
collection = bpy.data.collections.get("Asset_massing_shreve_hall_06d270a")
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
distances = [min(math.dist(p, tuple(q)) for q in base) for p in source_points]
if len(source_points) != 24 or max(distances) > 0.001:
    raise RuntimeError("Source footprint base points do not match within 1 mm")
coords = [obj.matrix_world @ v.co for v in obj.data.vertices]
result = {
    "saved_asset_reopened": True,
    "asset_id": "massing_shreve_hall_06d270a",
    "source_fid": attrs["FID"],
    "object_name": obj.name,
    "collection_object_count": len(collection.objects),
    "source_ring_vertex_count": len(source_points),
    "max_source_ring_error_m": round(max(distances), 8),
    "mesh_vertex_count": len(obj.data.vertices),
    "mesh_face_count": len(obj.data.polygons),
    "bounds_world_m": [[round(min(p[i] for p in coords), 6), round(max(p[i] for p in coords), 6)] for i in range(3)],
}
with open(os.path.join(folder, "shreve_reopen_check.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)
    f.write("\n")
print("SHREVE_REOPEN_JSON=" + json.dumps(result))
