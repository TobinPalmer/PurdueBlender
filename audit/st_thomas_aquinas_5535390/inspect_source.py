from __future__ import annotations

import json
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
scene = bpy.context.scene
coll = bpy.data.collections.get("Asset_massing_st_thomas_aquinas_5535390")
objects = list(coll.all_objects) if coll else []
records = []
mins = [float("inf")] * 3
maxs = [float("-inf")] * 3
for obj in objects:
    entry = {"name": obj.name, "type": obj.type,
             "location": list(obj.location), "rotation": list(obj.rotation_euler),
             "scale": list(obj.scale), "dimensions": list(obj.dimensions),
             "materials": [mat.name if mat else None for mat in obj.data.materials] if obj.type == "MESH" else []}
    if obj.type == "MESH":
        for corner in obj.bound_box:
            point = obj.matrix_world @ Vector(corner)
            for i in range(3):
                mins[i] = min(mins[i], float(point[i]))
                maxs[i] = max(maxs[i], float(point[i]))
    records.append(entry)
result = {"blend": bpy.data.filepath, "scene": scene.name, "collection": coll.name if coll else None,
          "object_count": len(objects), "objects": records,
          "bounds_world_m": [[mins[i], maxs[i]] for i in range(3)] if objects else None,
          "render": {"resolution": [scene.render.resolution_x, scene.render.resolution_y],
                     "engine": scene.render.engine}}
(OUT / "source_inventory.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
