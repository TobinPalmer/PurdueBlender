"""Reopen, measure, and independently write the expected ADDL collection."""
from pathlib import Path
import json
import bpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSET = ROOT / "modular/buildings/animal_disease_diagnostic_laboratory.blend"
PROBE = HERE / "collection_export_probe.blend"
EXPECTED = "Asset_animal_disease_diagnostic_laboratory"

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
assert bpy.context.scene.name == "Scene"
collection = bpy.data.collections.get(EXPECTED)
assert collection is not None
assert collection.get("building_id") == "animal_disease_diagnostic_laboratory"
assert collection.get("source_feature_id") == 241
assert collection.get("story_count") == 5
assert collection.get("campus_xy_m") == "[-196.355977, -1028.366531]"
assert len(collection.objects) == 8
assert all(obj.type not in {"CAMERA", "LIGHT"} for obj in collection.objects)

depsgraph = bpy.context.evaluated_depsgraph_get()
coords = []
shell_coords = []
mesh_objects = 0
external_images = []
for obj in collection.objects:
    assert tuple(round(v, 5) for v in obj.location) == (0, 0, 0) or obj.type == "FONT"
    if obj.type == "MESH":
        mesh_objects += 1
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        evaluated_points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
        coords.extend(evaluated_points)
        if obj.name == "ADDL_GIS_Footprint_Primary_Shell":
            shell_coords.extend(evaluated_points)
        evaluated.to_mesh_clear()
    for slot in obj.material_slots:
        material = slot.material
        if material and material.use_nodes:
            for node in material.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image and node.image.filepath:
                    external_images.append(node.image.filepath)

assert coords and mesh_objects >= 5
bounds = [[min(p[i] for p in coords), max(p[i] for p in coords)] for i in range(3)]
shell_bounds = [[min(p[i] for p in shell_coords), max(p[i] for p in shell_coords)] for i in range(3)]
assert abs(shell_bounds[0][0] - -19.8941) < 0.02 and abs(shell_bounds[0][1] - 19.4874) < 0.02
assert abs(shell_bounds[1][0] - -37.4791) < 0.02 and abs(shell_bounds[1][1] - 40.9016) < 0.02
assert abs(shell_bounds[2][0] - 0.35) < 0.02 and abs(shell_bounds[2][1] - 17.7236) < 0.02
assert not external_images

bpy.data.libraries.write(str(PROBE), {collection}, path_remap="RELATIVE_ALL", fake_user=True)
print(json.dumps({
    "reopened_asset": str(ASSET),
    "scene": bpy.context.scene.name,
    "collection": EXPECTED,
    "collection_objects": len(collection.objects),
    "mesh_objects": mesh_objects,
    "evaluated_world_bounds_m": bounds,
    "GIS_shell_bounds_m": shell_bounds,
    "external_image_paths": external_images,
    "collection_export_probe": str(PROBE),
}, indent=2))
