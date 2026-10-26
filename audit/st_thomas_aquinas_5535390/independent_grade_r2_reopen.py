"""Independent exact-SHA reopen/portability check for St. Thomas Aquinas R2."""
import hashlib
import json
from pathlib import Path

import bpy

OUT = Path(__file__).resolve().parent
ASSET = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_st_thomas_aquinas_5535390.blend")
EXPECTED_SHA = "9fea60330e434dc184d19c3397187c1171a47cbce23e624dbf39ca944a85b94a"
COLLECTION_NAME = "Asset_massing_st_thomas_aquinas_5535390"
ROOT_NAME = "AssetRoot_massing_st_thomas_aquinas_5535390"

actual_sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
if actual_sha != EXPECTED_SHA:
    raise RuntimeError(f"R2 file changed before grading: {actual_sha}")
scene = bpy.context.scene
collection = bpy.data.collections.get(COLLECTION_NAME)
root = bpy.data.objects.get(ROOT_NAME)
if collection is None:
    raise RuntimeError(f"Missing exported collection {COLLECTION_NAME}")
if root is None:
    raise RuntimeError(f"Missing root object {ROOT_NAME}")
objects = list(collection.all_objects)
mesh_objects = [obj for obj in objects if obj.type == "MESH"]
materialless = []
invalid_indices = []
mins = [float("inf")] * 3
maxs = [float("-inf")] * 3
depsgraph = bpy.context.evaluated_depsgraph_get()
for obj in mesh_objects:
    if not obj.material_slots:
        materialless.append(obj.name)
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        for poly in mesh.polygons:
            if poly.material_index >= len(evaluated.material_slots):
                invalid_indices.append(obj.name)
                break
        for vertex in mesh.vertices:
            point = evaluated.matrix_world @ vertex.co
            for axis in range(3):
                mins[axis] = min(mins[axis], float(point[axis]))
                maxs[axis] = max(maxs[axis], float(point[axis]))
    finally:
        evaluated.to_mesh_clear()
missing_images = []
image_records = []
for image in bpy.data.images:
    if image.source != "FILE" or not image.filepath:
        continue
    resolved = Path(bpy.path.abspath(image.filepath, library=image.library)).resolve()
    record = {"name": image.name, "path": image.filepath, "resolved_path": str(resolved), "packed": bool(image.packed_file)}
    image_records.append(record)
    if not image.packed_file and not resolved.exists():
        missing_images.append(record)
root_world = [[float(root.matrix_world[r][c]) for c in range(4)] for r in range(4)]
root_identity = all(abs(root_world[r][c] - (1.0 if r == c else 0.0)) < 1e-6 for r in range(4) for c in range(4))
libs = [lib.filepath for lib in bpy.data.libraries]
result = {
    "validation": "Independent fresh-process reopen in Blender 5.2.3 LTS",
    "asset": str(ASSET),
    "sha256": actual_sha,
    "hash_matches_requested": actual_sha == EXPECTED_SHA,
    "reopened_saved_asset": Path(bpy.data.filepath).resolve() == ASSET.resolve(),
    "scene": scene.name,
    "export_collection": collection.name,
    "collection_object_count": len(objects),
    "mesh_count": len(mesh_objects),
    "object_type_counts": {kind: sum(1 for obj in objects if obj.type == kind) for kind in sorted(set(obj.type for obj in objects))},
    "root": root.name,
    "root_world_matrix": root_world,
    "root_identity": root_identity,
    "bounds_asset_axis_major_m": [[mins[i], maxs[i]] for i in range(3)],
    "materialless_meshes": materialless,
    "invalid_material_index_meshes": sorted(set(invalid_indices)),
    "used_material_names": sorted({slot.material.name for obj in mesh_objects for slot in obj.material_slots if slot.material}),
    "missing_external_images": missing_images,
    "file_image_datablocks": image_records,
    "linked_libraries": libs,
    "placement_origin_custom_property": list(root.get("placement_origin_xy_m", [])),
    "coordinate_frame_property": root.get("coordinate_frame"),
    "evidence_scope": "Standalone asset only; master placement marker and neighboring geometry not reviewed.",
}
(OUT / "independent_grade_r2_reopen.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))
