import bpy
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(bpy.data.filepath).resolve().parent
MANIFEST = json.loads((ROOT / "modular" / "manifest.json").read_text(encoding="utf-8"))
CHECK_IDS = {
    "massing_beta_theta_pi_fid826",
    "massing_west_lafayette_intermediate_school_d72f0fa",
    "massing_west_lafayette_junior_senior_high_school_fa45bd1",
}
records = {record["id"]: record for record in MANIFEST["assets"] if record["id"] in CHECK_IDS}
scene = bpy.context.scene
root_children = list(scene.collection.children)
results = []
errors = []

for asset_id in sorted(CHECK_IDS):
    record = records.get(asset_id)
    if record is None:
        errors.append(f"manifest record missing: {asset_id}")
        continue
    collection = bpy.data.collections.get(record["collection"])
    if collection is None:
        errors.append(f"linked collection missing: {record['collection']}")
        continue
    direct_links = sum(child == collection for child in root_children)
    if direct_links != 1:
        errors.append(f"{asset_id}: expected one direct master link, found {direct_links}")
    if collection.library is None:
        errors.append(f"{asset_id}: collection is not linked from a library")
        linked_path = None
    else:
        linked_path = Path(bpy.path.abspath(collection.library.filepath)).resolve()
    expected_path = (ROOT / "modular" / record["file"]).resolve()
    if linked_path != expected_path:
        errors.append(f"{asset_id}: wrong library path {linked_path}; expected {expected_path}")
    objects = list(collection.all_objects)
    if len(objects) != record.get("object_count"):
        errors.append(f"{asset_id}: object count {len(objects)} != manifest {record.get('object_count')}")
    mesh_objects = [obj for obj in objects if obj.type == "MESH"]
    points = [obj.matrix_world @ Vector(corner)
              for obj in mesh_objects for corner in obj.bound_box]
    bounds = ([[min(point[i] for point in points), max(point[i] for point in points)]
               for i in range(3)] if points else None)
    expected_bounds = record.get("bounds_world_m")
    if bounds and expected_bounds:
        max_error = max(abs(bounds[i][j] - expected_bounds[i][j])
                        for i in range(3) for j in range(2))
        if max_error > 0.01:
            errors.append(f"{asset_id}: world bounds differ from manifest by {max_error:.6f} m")
    else:
        max_error = None
    results.append({
        "id": asset_id,
        "collection": collection.name,
        "direct_master_links": direct_links,
        "library_path": str(linked_path) if linked_path else None,
        "expected_library_path": str(expected_path),
        "object_count": len(objects),
        "mesh_count": len(mesh_objects),
        "bounds_world_m": bounds,
        "max_manifest_bounds_error_m": max_error,
        "accuracy_status": record.get("accuracy_status"),
    })

report = {
    "status": "PASS" if not errors else "FAIL",
    "master_file": str(Path(bpy.data.filepath).resolve()),
    "fresh_open_blender_version": bpy.app.version_string,
    "scene": scene.name,
    "scene_object_count": len(scene.objects),
    "checked_building_count": len(results),
    "results": results,
    "errors": errors,
}
out = ROOT / "audit" / "master_integration_2026-10-27_buildings.json"
out.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report))
if errors:
    raise RuntimeError("Master link verification failed: " + "; ".join(errors))
