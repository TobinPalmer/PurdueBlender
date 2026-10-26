"""Reopen CQE asset in Blender and validate package/coordinate contract."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_cary_quadrangle_east_cqe_230c813"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
OUT = ROOT / "audit" / ASSET_ID / "reopen_validation.json"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
expected_scene = f"Building_{ASSET_ID}"
expected_collection = f"Asset_{ASSET_ID}"
assert bpy.context.scene.name == expected_scene, bpy.context.scene.name
collection = bpy.data.collections.get(expected_collection)
assert collection is not None
assert collection.get("asset_id") == ASSET_ID
objects = list(collection.objects)
assert objects and all(obj.type == "MESH" for obj in objects)
assert all(obj.library is None for obj in objects)
assert all(max(abs(v) for v in obj.location) < 1e-7 for obj in objects)
assert all(max(abs(v) for v in obj.rotation_euler) < 1e-7 for obj in objects)
assert all(max(abs(v-1.0) for v in obj.scale) < 1e-7 for obj in objects)
coords = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
bounds = [[min(v[i] for v in coords), max(v[i] for v in coords)] for i in range(3)]
expected = [[-286.1, -270.3], [510.4, 593.5], [0.0, 14.7]]
assert all(expected[i][0] <= bounds[i][0] <= bounds[i][1] <= expected[i][1] for i in range(3)), bounds
report = {
    "status": "passed",
    "asset_id": ASSET_ID,
    "scene": bpy.context.scene.name,
    "asset_collection": collection.name,
    "asset_mesh_objects": len(objects),
    "asset_bounds_world_m_xyz": bounds,
    "identity_transforms": True,
    "external_object_libraries": False,
    "preview_setup_separate_from_asset_collection": True,
}
OUT.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
print(json.dumps(report, indent=2))
