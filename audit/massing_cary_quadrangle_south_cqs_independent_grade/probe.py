import bpy
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_cary_quadrangle_south_cqs_7ee2283"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
OUT = Path(__file__).resolve().parent

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene_name = f"Building_{ASSET_ID}"
coll_name = f"Asset_{ASSET_ID}"
scene = bpy.data.scenes.get(scene_name)
coll = bpy.data.collections.get(coll_name)
assert scene is not None, f"Missing scene {scene_name}"
assert coll is not None, f"Missing collection {coll_name}"
objects = list(coll.objects)
assert len(objects) == 1, f"Expected one exported object, got {len(objects)}"
obj = objects[0]
assert obj.type == "MESH", f"Expected mesh, got {obj.type}"
depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated = obj.evaluated_get(depsgraph)
mesh = evaluated.to_mesh()
verts = [evaluated.matrix_world @ v.co for v in mesh.vertices]
edge_use = {}
for poly in mesh.polygons:
    for edge in poly.edge_keys:
        edge_use[tuple(sorted(edge))] = edge_use.get(tuple(sorted(edge)), 0) + 1
all_bounds = [[min(v[i] for v in verts), max(v[i] for v in verts)] for i in range(3)]
ground = [(v.x, v.y) for v in verts if abs(v.z) < 1e-5]
ground_bounds = [[min(p[0] for p in ground), max(p[0] for p in ground)],
                 [min(p[1] for p in ground), max(p[1] for p in ground)]] if ground else []
result = {
    "opened_asset": str(ASSET.relative_to(ROOT)),
    "scene": scene.name,
    "collection": coll.name,
    "collection_object_count": len(objects),
    "object_name": obj.name,
    "object_type": obj.type,
    "stable_building_id": obj.get("stable_building_id"),
    "source_feature_property": obj.get("source_feature"),
    "location": list(obj.location),
    "rotation_euler": list(obj.rotation_euler),
    "scale": list(obj.scale),
    "collection_instance_offset": list(coll.instance_offset),
    "bounds_world_m": all_bounds,
    "ground_vertex_count": len(ground),
    "ground_vertex_bounds_m": ground_bounds,
    "vertex_count": len(mesh.vertices),
    "polygon_count": len(mesh.polygons),
    "material_names": [m.name if m else None for m in obj.data.materials],
    "modifier_count": len(obj.modifiers),
    "boundary_edges": sum(v == 1 for v in edge_use.values()),
    "nonmanifold_edges": sum(v != 2 for v in edge_use.values()),
    "custom_properties": {k: obj[k] for k in obj.keys()},
}
evaluated.to_mesh_clear()
(OUT / "probe.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
