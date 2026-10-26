"""Read-only fresh-open probe of the Drug Discovery master instance."""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

asset_id = "massing_purdue_drug_discovery_facility_fc72a4a"
marker_name = "Placement_" + asset_id
marker = bpy.data.objects.get(marker_name)
manifest_path = Path(bpy.data.filepath).parent / "modular" / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
record = next((a for a in manifest["assets"] if a["id"] == asset_id), None)

def collection_local_matrix(obj, cache):
    if obj in cache:
        return cache[obj]
    mat = obj.matrix_local.copy()
    if obj.parent is not None:
        mat = collection_local_matrix(obj.parent, cache) @ mat
    cache[obj] = mat
    return mat

def record_bounds(collection, marker):
    points = []
    matrices = {}
    for obj in collection.all_objects:
        if obj.type not in {"MESH", "CURVE", "FONT"}:
            continue
        local = collection_local_matrix(obj, matrices)
        for corner in obj.bound_box:
            points.append(marker.matrix_world @ (local @ Vector(corner)))
    if not points:
        return None
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]

markers = [o for o in bpy.data.objects if o.name == marker_name]
collection = marker.instance_collection if marker else None
linked_path = None
if collection is not None and collection.library is not None:
    linked_path = bpy.path.abspath(collection.library.filepath)
result = {
    "blender_version": bpy.app.version_string,
    "master_path": bpy.data.filepath,
    "scene_object_count": len(bpy.context.scene.objects),
    "exact_marker_count": len(markers),
    "marker_found": marker is not None,
    "marker_location": list(marker.location) if marker else None,
    "marker_rotation_euler": list(marker.rotation_euler) if marker else None,
    "marker_scale": list(marker.scale) if marker else None,
    "marker_instance_type": marker.instance_type if marker else None,
    "instance_collection": collection.name if collection else None,
    "library_path": linked_path,
    "record_kind": record.get("kind") if record else None,
    "record_file": record.get("file") if record else None,
    "expected_placement_xy": record.get("placement_origin_xy_m") if record else None,
    "expected_local_bounds": record.get("local_bounds_m") if record else None,
    "actual_world_bounds": record_bounds(collection, marker) if collection and marker else None,
    "expected_world_bounds": record.get("bounds_world_m") if record else None,
    "direct_root_collection_link": collection in list(bpy.context.scene.collection.children) if collection else False,
}
target = Path(sys.argv[sys.argv.index("--") + 1])
target.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result))
