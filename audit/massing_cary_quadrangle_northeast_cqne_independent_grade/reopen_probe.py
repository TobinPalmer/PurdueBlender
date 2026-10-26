"""Open the submitted CQNE .blend independently and record evaluated geometry."""
import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
ID = "massing_cary_quadrangle_northeast_cqne_0a76fca"
asset = ROOT / "modular" / "buildings" / f"{ID}.blend"
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene_name = f"Building_{ID}"
collection_name = f"Asset_{ID}"
scene = bpy.data.scenes.get(scene_name)
collection = bpy.data.collections.get(collection_name)
assert scene is not None, f"missing scene: {scene_name}"
assert collection is not None, f"missing collection: {collection_name}"
depsgraph = bpy.context.evaluated_depsgraph_get()
points = []
for obj in collection.objects:
    if obj.type == "MESH":
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        points.extend(evaluated.matrix_world @ vertex.co for vertex in mesh.vertices)
        evaluated.to_mesh_clear()
assert points, "collection has no evaluated mesh vertices"
mins = [min(p[i] for p in points) for i in range(3)]
maxs = [max(p[i] for p in points) for i in range(3)]
report = {
    "asset": str(asset.relative_to(ROOT)).replace("\\", "/"),
    "loaded_scene": scene.name,
    "loaded_collection": collection.name,
    "object_count": len(collection.objects),
    "mesh_count": sum(obj.type == "MESH" for obj in collection.objects),
    "evaluated_world_bounds_m": [[round(v, 6) for v in mins], [round(v, 6) for v in maxs]],
    "evaluated_world_dimensions_m": [round(maxs[i] - mins[i], 6) for i in range(3)],
    "status": "PASS: saved asset reopened and expected collection evaluated",
}
out = Path(__file__).with_name("reopen_probe.json")
out.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
