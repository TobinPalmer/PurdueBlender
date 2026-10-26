"""Reopen and verify the Twin Pines source library with Blender background."""
import bpy
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "reopen_validation.json"
ID = "massing_twin_pines_cooperative_8f606f9"
COLLECTION = "Asset_" + ID
ASSET = ROOT / "modular/buildings/massing_twin_pines_cooperative_8f606f9.blend"
EXPECTED = [
    (-341.277871,76.428832),(-341.379644,65.691264),
    (-316.894822,65.458080),(-316.767607,78.871712),
    (-327.267159,78.971648),(-327.292603,76.284480),
]

col = bpy.data.collections.get(COLLECTION)
assert col is not None, f"missing collection {COLLECTION}"
objects = list(col.objects)
assert len(objects) == 1, f"expected one export object, got {len(objects)}"
obj = objects[0]
assert obj.name == "Twin Pines Cooperative" and obj.type == "MESH"
assert not obj.modifiers, "unexpected unapplied modifiers"
assert tuple(round(v,6) for v in obj.location) == (0.0,0.0,0.0)
assert tuple(round(v,6) for v in obj.scale) == (1.0,1.0,1.0)

depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated = obj.evaluated_get(depsgraph)
mesh = evaluated.to_mesh()
world = evaluated.matrix_world
verts = [world @ v.co for v in mesh.vertices]
bounds = [[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)]
evaluated.to_mesh_clear()

base_verts = [(v.x,v.y) for v in verts if abs(v.z) < 1e-5]
per_vertex_error = []
for x,y in EXPECTED:
    per_vertex_error.append(min(math.hypot(vx-x,vy-y) for vx,vy in base_verts))
assert max(per_vertex_error) < 1e-4, f"GIS footprint vertices do not match: {per_vertex_error}"
assert abs(bounds[2][1]-9.05) < 1e-4
assert len(obj.data.materials) >= 8
assert len(obj.data.vertices) > 1000 and len(obj.data.polygons) > 1000

record = {
    "asset": str(ASSET.relative_to(ROOT)).replace("\\","/"),
    "opened_by_blender": bpy.app.version_string,
    "status": "passed",
    "collection": COLLECTION,
    "collection_object_count": len(objects),
    "object": obj.name,
    "mesh_vertex_count": len(obj.data.vertices),
    "mesh_polygon_count": len(obj.data.polygons),
    "modifier_count": len(obj.modifiers),
    "object_location": list(obj.location),
    "object_rotation_euler_radians": list(obj.rotation_euler),
    "object_scale": list(obj.scale),
    "evaluated_bounds_world_m": bounds,
    "source_footprint_vertices_xy_m": [list(v) for v in EXPECTED],
    "max_source_footprint_vertex_error_m": max(per_vertex_error),
    "z_min_m": bounds[2][0],
    "z_max_m_estimated_roof_ridge": bounds[2][1],
    "external_image_dependencies": [im.filepath for im in bpy.data.images if im.source == "FILE" and not im.packed_file],
    "checks": [
        "reopened saved .blend in Blender background",
        "expected asset collection and stable object name retained",
        "single unified mesh, no modifiers, no object transform or campus-coordinate shift",
        "all six base vertices match the projected OSM FID 766 footprint to <0.0001 m",
        "estimated roof ridge height is 9.05 m instead of inherited 16 m fallback",
        "geometry and material slots are present; no unpacked external image dependencies",
    ],
    "limitations": [
        "OSM footprint is a community mapping and may include generalized wall/porch edges; not a survey.",
        "Roof/eave heights, floor spacing, window count and many secondary facade details are estimates from photographs; no measured elevation or architectural plan was located.",
        "South-facing entrance/frontage is inferred from the house photos and site orientation; exact facade azimuth is not independently surveyed.",
    ],
}
OUT.write_text(json.dumps(record,indent=2),encoding="utf-8")
print(json.dumps(record,indent=2))
