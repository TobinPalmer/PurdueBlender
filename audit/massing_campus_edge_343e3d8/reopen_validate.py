"""Reopen and validate the Campus Edge source library in background Blender."""
import bpy
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_campus_edge_343e3d8"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
OUT = ROOT / "audit" / ASSET_ID / "reopen_validation.json"
ROOF_ZONE_ANALYSIS = ROOT / "audit" / ASSET_ID / "campus_edge_roof_zone_analysis.json"
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
podium_bounds = object_bounds[shell.name]
assert math.isclose(podium_bounds["min"][2], 0.0, abs_tol=1e-5)
assert math.isclose(podium_bounds["max"][2], 4.8, abs_tol=1e-4)
assert total_bounds["max"][2] > 36.0
for zone in ("North", "Middle", "South"):
    shell_obj = collection.objects.get(f"CE_{zone}_Tower_Shell")
    roof_obj = collection.objects.get(f"CE_{zone}_Tower_Roof_Parapet")
    assert shell_obj is not None and roof_obj is not None
    assert object_bounds[shell_obj.name]["max"][2] < object_bounds[roof_obj.name]["max"][2]
assert collection.objects.get("CE_Residential_Tower_Shell") is None, "Legacy continuous tower shell remains"
assert len([obj for obj in collection.objects if obj.type == "MESH"]) == 15
roof_zone_data = json.loads(ROOF_ZONE_ANALYSIS.read_text(encoding="utf-8"))["zones"]
tower_roof_bounds = {}
for key, name in (("north", "North"), ("middle", "Middle"), ("south", "South")):
    shell_bounds = object_bounds[f"CE_{name}_Tower_Shell"]
    roof_bounds = object_bounds[f"CE_{name}_Tower_Roof_Parapet"]
    expected_y_min, expected_y_max = roof_zone_data[key]["local_y_bounds_m"]
    expected_y_min = max(expected_y_min, podium_bounds["min"][1])
    expected_y_max = min(expected_y_max, podium_bounds["max"][1])
    assert abs(shell_bounds["min"][1] - expected_y_min) < 0.02
    assert abs(shell_bounds["max"][1] - expected_y_max) < 0.02
    expected_roof_z = roof_zone_data[key]["roof_surface_datum_estimate_m"]
    assert abs(roof_bounds["max"][2] - expected_roof_z) < 0.01
    tower_roof_bounds[key] = {
        "shell_bounds_m": shell_bounds,
        "roof_bounds_m": roof_bounds,
        "ndhm_zone_sample_count": roof_zone_data[key]["ndhm_sample_count"],
        "approximate_roof_surface_median_m": expected_roof_z,
    }

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
    "structural_podium_bounds_m": podium_bounds,
    "tower_roof_zone_bounds": tower_roof_bounds,
    "preview_setup_objects_outside_asset_collection": len(preview_collection.objects),
    "checks": {
        "scene_and_export_collection_names": "pass",
        "stable_asset_id_and_coordinate_contract": "pass",
        "local_portable_mesh_asset": "pass",
        "evaluated_world_bounds": "pass",
        "separate_preview_setup": "pass",
        "approximate_height_over_36m": "pass",
        "three_separated_roof_towers": "pass",
        "legacy_continuous_shell_removed": "pass",
        "roof_shells_match_orthophoto_interpretation_bands": "pass",
    },
    "height_interpretation": "Per-zone NDHM medians (north {north:.3f} m, middle {middle:.3f} m, south {south:.3f} m) are approximate normalized roof-surface statistics in orthophoto-interpreted bands; they do not establish eaves, story counts, or surveyed tower heights.".format(
        north=roof_zone_data["north"]["roof_surface_datum_estimate_m"],
        middle=roof_zone_data["middle"]["roof_surface_datum_estimate_m"],
        south=roof_zone_data["south"]["roof_surface_datum_estimate_m"],
    ),
}
OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
