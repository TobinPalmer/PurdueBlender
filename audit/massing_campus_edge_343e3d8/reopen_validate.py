"""Reopen and validate the Campus Edge source library in background Blender."""
import bpy
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_campus_edge_343e3d8"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
OUT = ROOT / "audit" / ASSET_ID / "reopen_validation.json"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
SCENE_NAME = f"Building_{ASSET_ID}"

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
collection = bpy.data.collections.get(COLLECTION_NAME)
assert scene.name == SCENE_NAME, (scene.name, SCENE_NAME)
assert collection is not None, COLLECTION_NAME
assert collection.get("asset_id") == ASSET_ID
assert collection.get("coordinate_contract", "").startswith("Simple massing asset in campus world coordinates")
assert len(collection.objects) > 0
assert all(obj.type == "MESH" for obj in collection.objects), "Asset collection includes a non-mesh object"
assert all(not obj.library for obj in collection.objects), "Asset has linked objects"
assert not bpy.data.libraries, "Asset contains linked libraries"
assert all(image.packed_file or not image.filepath for image in bpy.data.images), "Asset contains an unpacked external image"

depsgraph = bpy.context.evaluated_depsgraph_get()
object_bounds = {}
all_points = []
for obj in collection.objects:
    evaluated = obj.evaluated_get(depsgraph)
    coords = [evaluated.matrix_world @ __import__("mathutils").Vector(corner) for corner in evaluated.bound_box]
    object_bounds[obj.name] = {
        "min": [min(p[i] for p in coords) for i in range(3)],
        "max": [max(p[i] for p in coords) for i in range(3)],
        "vertices": len(evaluated.data.vertices),
    }
    all_points.extend(coords)

total_bounds = {
    "min": [min(p[i] for p in all_points) for i in range(3)],
    "max": [max(p[i] for p in all_points) for i in range(3)],
}
shell = bpy.data.objects.get("CE_Continuous_Brick_Podium")
assert collection.objects.get(shell.name) == shell
shell_bounds = object_bounds[shell.name]
assert math.isclose(shell_bounds["min"][2], 0.0, abs_tol=1e-5)
assert math.isclose(shell_bounds["max"][2], 4.8, abs_tol=1e-4)
assert total_bounds["max"][2] > 36.0
assert len([obj for obj in collection.objects if obj.type == "MESH"]) == 11

preview_collection = bpy.data.collections.get("Campus_Edge_Preview_Setup")
assert preview_collection is not None
assert not set(preview_collection.objects) & set(collection.objects)

result = {
    "asset_path": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
    "opened_by_blender": bpy.app.version_string,
    "scene": scene.name,
    "collection": collection.name,
    "asset_id": collection["asset_id"],
    "asset_objects": len(collection.objects),
    "asset_mesh_objects": len([obj for obj in collection.objects if obj.type == "MESH"]),
    "all_asset_objects_are_local_meshes": True,
    "linked_libraries": 0,
    "external_unpacked_images": 0,
    "asset_bounds_m": total_bounds,
    "structural_podium_bounds_m": shell_bounds,
    "preview_setup_objects_outside_asset_collection": len(preview_collection.objects),
    "checks": {
        "scene_and_export_collection_names": "pass",
        "stable_asset_id_and_coordinate_contract": "pass",
        "local_portable_mesh_asset": "pass",
        "evaluated_world_bounds": "pass",
        "separate_preview_setup": "pass",
        "approximate_height_over_36m": "pass",
    },
    "height_interpretation": "36.12 m approximate roof datum inferred from 2018 NDHM statistics; not a surveyed eave or floor datum.",
}
OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
