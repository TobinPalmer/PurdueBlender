"""Fresh-process check for the Sigma Phi Epsilon library asset."""
import json
import math
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_house_301841250_d63b09a"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
OUT = Path(__file__).with_name("reopen_validation.json")
SOURCE = Path(__file__).with_name("sources") / "osm_way_301841250.json"

if bpy.data.filepath != str(ASSET):
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))

collection_name = f"Asset_{ASSET_ID}"
scene_name = f"Building_{ASSET_ID}"
collection = bpy.data.collections.get(collection_name)
scene = bpy.data.scenes.get(scene_name)
shell = bpy.data.objects.get("House_301841250")
assert collection is not None, f"Missing exported collection {collection_name}"
assert scene is not None, f"Missing asset scene {scene_name}"
assert shell is not None and shell.type == "MESH", "Missing base footprint shell"
assert shell.name in collection.objects, "Base shell is outside the export collection"

with SOURCE.open(encoding="utf-8") as stream:
    source = json.load(stream)
ring = source["geometry_local_m"]["coordinates"][0][:-1]
depsgraph = bpy.context.evaluated_depsgraph_get()
shell_eval = shell.evaluated_get(depsgraph)
mesh = shell_eval.to_mesh()
base_xy = [tuple((shell.matrix_world @ v.co)[:2]) for v in mesh.vertices if abs((shell.matrix_world @ v.co).z) < 1e-5]
nearest_errors = []
for px, py in ring:
    nearest_errors.append(min(math.hypot(p[0] - px, p[1] - py) for p in base_xy))
shell_eval.to_mesh_clear()

mins = [float("inf")] * 3
maxs = [float("-inf")] * 3
mesh_count = 0
face_count = 0
modifier_count = 0
for obj in collection.all_objects:
    modifier_count += len(obj.modifiers)
    if obj.type != "MESH":
        continue
    mesh_count += 1
    obj_eval = obj.evaluated_get(depsgraph)
    eval_mesh = obj_eval.to_mesh()
    face_count += len(eval_mesh.polygons)
    for vertex in eval_mesh.vertices:
        co = obj_eval.matrix_world @ vertex.co
        for axis in range(3):
            mins[axis] = min(mins[axis], float(co[axis]))
            maxs[axis] = max(maxs[axis], float(co[axis]))
    obj_eval.to_mesh_clear()

missing_images = []
for image in bpy.data.images:
    if image.source == "FILE" and image.filepath and not image.packed_file:
        path = Path(bpy.path.abspath(image.filepath))
        if not path.exists():
            missing_images.append(str(path))

shell_world_bounds = [[float(min((shell.matrix_world @ v.co)[axis] for v in shell.data.vertices)),
                       float(max((shell.matrix_world @ v.co)[axis] for v in shell.data.vertices))]
                      for axis in range(3)]
result = {
    "asset_id": ASSET_ID,
    "asset_path": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
    "fresh_process_reopen": True,
    "blend_version": list(bpy.app.version),
    "scene": scene.name,
    "export_collection": collection.name,
    "export_object_count": len(collection.all_objects),
    "export_mesh_count": mesh_count,
    "export_face_count": face_count,
    "modifier_count": modifier_count,
    "evaluated_export_bounds_world_m": [[mins[i], maxs[i]] for i in range(3)],
    "shell_bounds_world_m": shell_world_bounds,
    "source_way_id": source["way_id"],
    "source_ring_vertex_count": len(ring),
    "source_ring_max_nearest_vertex_error_m": max(nearest_errors),
    "shell_world_matrix_identity_error": max(abs(shell.matrix_world[i][j] - (1.0 if i == j else 0.0))
                                               for i in range(4) for j in range(4)),
    "unpacked_missing_image_paths": missing_images,
    "checks": {
        "asset_scene_and_export_collection_present": True,
        "base_shell_source_ring_matches_within_0_001m": max(nearest_errors) <= 0.001,
        "shell_transform_is_identity_campus_frame": max(abs(shell.matrix_world[i][j] - (1.0 if i == j else 0.0)) for i in range(4) for j in range(4)) < 1e-6,
        "evaluated_export_is_nonempty": mesh_count > 0 and face_count > 0,
        "no_unpacked_missing_external_images": not missing_images,
        "roof_peak_is_estimated_below_13m": maxs[2] < 13.0,
    },
    "validation_date": "2026-10-26",
}
result["all_checks_pass"] = all(result["checks"].values())
OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
if not result["all_checks_pass"]:
    raise RuntimeError("One or more fresh-process validation checks failed")
