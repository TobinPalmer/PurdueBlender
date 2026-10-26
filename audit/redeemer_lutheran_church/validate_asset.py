import bpy
import json
import math
import os

folder = os.path.dirname(__file__)
with open(os.path.join(folder, "source_mesh_snapshot.json"), encoding="utf-8-sig") as f:
    snapshot = json.load(f)
asset_id = snapshot["asset_id"]
obj = bpy.data.objects.get(snapshot["object"])
collection = bpy.data.collections.get("Asset_" + asset_id)
if obj is None or collection is None or obj not in collection.objects[:] or len(collection.objects) != 1:
    raise RuntimeError("Assigned object or collection structure is invalid")

source_ring = []
for v in snapshot["vertices_local"]:
    if abs(v[2]) < 1e-6:
        p = (round(v[0], 6), round(v[1], 6), 0.0)
        if p not in source_ring:
            source_ring.append(p)
mesh_base = [obj.matrix_world @ v.co for v in obj.data.vertices if abs((obj.matrix_world @ v.co).z) < 1e-5]
if len(source_ring) != 24 or len(mesh_base) < len(source_ring):
    raise RuntimeError("Could not locate all preserved source-ring base vertices")
distances = [min(math.dist(p, tuple(q)) for q in mesh_base) for p in source_ring]
if max(distances) > 0.001:
    raise RuntimeError(f"Source footprint differs by {max(distances):.6f} m")
coords = [obj.matrix_world @ v.co for v in obj.data.vertices]
result = {
    "opened": True,
    "asset_id": asset_id,
    "object": obj.name,
    "collection_objects": len(collection.objects),
    "source_ring_vertices": len(source_ring),
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
