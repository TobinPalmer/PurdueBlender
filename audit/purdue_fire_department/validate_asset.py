import bpy
import hashlib
import json
import os
from mathutils import Vector

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
asset_id = "massing_purdue_fire_department_520430b"
asset_path = os.path.join(root, "modular", "buildings", asset_id + ".blend")
collection_name = "Asset_" + asset_id
scene_name = "Building_" + asset_id
bpy.ops.wm.open_mainfile(filepath=asset_path)
coll = bpy.data.collections.get(collection_name)
assert coll is not None, "Expected asset collection missing"
assert bpy.context.scene.name == scene_name, "Scene name mismatch"
meshes = [o for o in coll.all_objects if o.type == "MESH"]
asset_objects = {o.name for o in coll.all_objects}
assert len(meshes) >= 50, f"Expected detailed asset, found {len(meshes)} meshes"
assert all(o.data.materials for o in meshes), "At least one mesh has no material"
deps = bpy.context.evaluated_depsgraph_get()
coords = []
for obj in meshes:
    ev = obj.evaluated_get(deps)
    for corner in ev.bound_box:
        coords.append(ev.matrix_world @ Vector(corner))
bounds = [[min(v[i] for v in coords), max(v[i] for v in coords)] for i in range(3)]
image_paths = []
for image in bpy.data.images:
    if image.source == "FILE":
        image_paths.append({"name": image.name, "filepath": image.filepath, "packed": image.packed_file is not None})
with open(asset_path, "rb") as f:
    sha = hashlib.sha256(f.read()).hexdigest()
report = {
    "asset_id": asset_id,
    "asset_path": os.path.relpath(asset_path, root).replace("\\", "/"),
    "asset_sha256": sha,
    "scene": bpy.context.scene.name,
    "collection": coll.name,
    "mesh_object_count": len(meshes),
    "object_count_all_types": len(list(coll.all_objects)),
    "objects_outside_asset_collection": [o.name for o in bpy.context.scene.objects if o.name not in asset_objects],
    "assigned_material_meshes": sum(1 for o in meshes if len(o.data.materials) > 0),
    "material_names": sorted({m.name for o in meshes for m in o.data.materials if m}),
    "world_bounds_m": bounds,
    "external_image_paths": image_paths,
    "verified_after_fresh_open": True
}
out = os.path.join(os.path.dirname(__file__), "asset_validation.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
print(json.dumps(report, indent=2))
