from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/rawls_hall.blend"
OUT = Path(__file__).with_name("outliers_round8.json")
bpy.ops.wm.open_mainfile(filepath=str(ASSET))


def box(points):
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]


items = []
root = bpy.data.objects.get("AssetRoot_rawls_hall")
root_record = None
if root:
    root_record = {
        "location": list(root.location),
        "rotation": list(root.rotation_euler),
        "scale": list(root.scale),
        "matrix_local": [list(row) for row in root.matrix_local],
        "matrix_world": [list(row) for row in root.matrix_world],
        "parent": root.parent.name if root.parent else None,
    }
for obj in bpy.data.objects:
    world = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    wb = box(world)
    if max(abs(value) for axis in wb for value in axis) > 100:
        local_verts = [list(v.co) for v in obj.data.vertices] if obj.type == "MESH" else []
        items.append({
            "name": obj.name,
            "type": obj.type,
            "location": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale),
            "matrix_local": [list(row) for row in obj.matrix_local],
            "matrix_world": [list(row) for row in obj.matrix_world],
            "parent": obj.parent.name if obj.parent else None,
            "parent_matrix_world": [list(row) for row in obj.parent.matrix_world] if obj.parent else None,
            "matrix_parent_inverse": [list(row) for row in obj.matrix_parent_inverse],
            "hide_viewport": obj.hide_viewport,
            "hide_render": obj.hide_render,
            "world_bounds": wb,
            "local_vertex_bounds": box([Vector(v) for v in local_verts]) if local_verts else None,
            "vertex_count": len(local_verts),
            "faces": len(obj.data.polygons) if obj.type == "MESH" else None,
        })
OUT.write_text(json.dumps({"root": root_record, "outliers": items}, indent=2), encoding="utf-8")
print(f"Wrote {OUT}; {len(items)} outliers")
