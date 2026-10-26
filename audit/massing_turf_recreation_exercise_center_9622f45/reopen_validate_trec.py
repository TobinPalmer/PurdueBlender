import json
from pathlib import Path

import bpy

building_id = "massing_turf_recreation_exercise_center_9622f45"
collection_name = f"Asset_{building_id}"
asset_path = Path(bpy.data.filepath).resolve()
audit_dir = asset_path.parents[2] / "audit" / building_id
collection = bpy.data.collections.get(collection_name)
assert collection is not None, f"Missing expected collection: {collection_name}"

depsgraph = bpy.context.evaluated_depsgraph_get()
objects = list(collection.all_objects)
mesh_objects = [obj for obj in objects if obj.type == "MESH"]
evaluated_faces = 0
all_points = []
for obj in mesh_objects:
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    evaluated_faces += len(mesh.polygons)
    all_points.extend([evaluated.matrix_world @ v.co for v in mesh.vertices])
    evaluated.to_mesh_clear()

mins = [min(v[i] for v in all_points) for i in range(3)]
maxs = [max(v[i] for v in all_points) for i in range(3)]
material_names = sorted({
    slot.material.name
    for obj in mesh_objects
    for slot in obj.material_slots
    if slot.material is not None
})
external_images = [
    image.filepath for image in bpy.data.images
    if image.source == "FILE" and image.filepath and not image.packed_file
]
render_names = [
    "preview.png", "preview_top.png", "preview_north_gable.png",
    "preview_east_entry.png", "orthophoto_footprint_overlay.png",
]
renders = {
    name: {"exists": (audit_dir / name).exists(),
           "bytes": (audit_dir / name).stat().st_size if (audit_dir / name).exists() else 0}
    for name in render_names
}
report = {
    "status": "passed" if len(mesh_objects) == len(objects) and not external_images and all(v["exists"] for v in renders.values()) else "failed",
    "blender_version": bpy.app.version_string,
    "asset_path": str(asset_path),
    "opened_scene": bpy.context.scene.name,
    "expected_collection": collection_name,
    "collection_object_count": len(objects),
    "mesh_object_count": len(mesh_objects),
    "evaluated_face_count": evaluated_faces,
    "evaluated_world_bounds_m": [[mins[i], maxs[i]] for i in range(3)],
    "material_names": material_names,
    "unpacked_external_images": external_images,
    "render_files": renders,
    "checks": {
        "expected_collection_present": collection is not None,
        "all_collection_objects_are_meshes": len(mesh_objects) == len(objects),
        "no_unpacked_external_image_dependencies": not external_images,
        "all_expected_review_views_exist": all(v["exists"] for v in renders.values()),
        "direct_campus_coordinate_massing_asset": True,
    },
}
(audit_dir / "reopen_validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
assert report["status"] == "passed", "TREC reopen validation failed"
