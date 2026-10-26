from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/rawls_hall.blend"
OUT = Path(__file__).with_name("inspection_round8.json")
bpy.ops.wm.open_mainfile(filepath=str(ASSET))


def bounds_world(obj):
    pts = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)]


items = []
for obj in bpy.data.objects:
    if "Window" in obj.name or "Glazing" in obj.name or "Glass" in obj.name:
        if any(tag in obj.name for tag in ("South", "North", "RAWL_Curtain")):
            mats = [slot.material for slot in obj.material_slots]
            items.append({
                "name": obj.name,
                "type": obj.type,
                "bounds": bounds_world(obj),
                "dimensions": list(obj.dimensions),
                "mesh_vertices": len(obj.data.vertices) if obj.type == "MESH" else None,
                "mesh_faces": len(obj.data.polygons) if obj.type == "MESH" else None,
                "materials": [{
                    "name": mat.name,
                    "surface_render_method": getattr(mat, "surface_render_method", None),
                    "diffuse_color": list(mat.diffuse_color),
                    "principled": [{
                        "base_color": list(next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"].default_value),
                        "alpha": float(next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Alpha"].default_value),
                        "transmission": float(next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Transmission Weight"].default_value),
                        "roughness": float(next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Roughness"].default_value),
                    } for _ in [0] if mat.use_nodes and any(n.type == "BSDF_PRINCIPLED" for n in mat.node_tree.nodes)],
                } for mat in mats if mat is not None],
            })

plan = []
for obj in bpy.data.objects:
    if "RAWL_2026_Plan" in obj.name or obj.name in {"RAWL_Masonry_Exterior_Walls", "RAWL_North_Windows_Glass", "RAWL_South_Windows_South_Glass"}:
        plan.append({"name": obj.name, "bounds": bounds_world(obj), "type": obj.type})

data = {"asset": str(ASSET), "scene": bpy.context.scene.name, "objects": items, "plan_and_shell": plan}
OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
print(f"Wrote {OUT} with {len(items)} glazing/window objects and {len(plan)} plan/shell objects")
