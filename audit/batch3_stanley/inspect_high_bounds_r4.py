"""Read-only independent listing of Stanley meshes extending above the reported roof bounds."""
import json
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
collection = bpy.data.collections.get("Asset_stanley_coulter_hall")
if collection is None:
    raise RuntimeError("Expected asset collection not found")
items = []
for obj in collection.all_objects:
    if obj.type != "MESH":
        continue
    pts = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    zmin, zmax = min(p.z for p in pts), max(p.z for p in pts)
    if zmax > 15.9:
        items.append({
            "name": obj.name,
            "z_min": zmin,
            "z_max": zmax,
            "hide_render": bool(obj.hide_render),
            "hide_viewport": bool(obj.hide_viewport),
            "hide_get": bool(obj.hide_get()),
        })
items.sort(key=lambda item: item["z_max"], reverse=True)
out = {"asset": bpy.data.filepath, "threshold_z": 15.9, "count": len(items), "objects": items}
Path(ROOT / "audit/batch3_stanley/independent_high_bounds_r4.json").write_text(
    json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)
print(json.dumps(out, indent=2, ensure_ascii=False))
