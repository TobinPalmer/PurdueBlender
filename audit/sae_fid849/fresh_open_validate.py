"""Read-only fresh-open audit for the FID 849 asset."""
import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector

root = Path(__file__).resolve().parents[2]
asset = root / "modular" / "buildings" / "massing_sigma_alpha_epsilon_fid849.blend"
out = root / "audit" / "sae_fid849" / "fresh_open_inspection.json"
collection_name = "Asset_massing_sigma_alpha_epsilon_fid849"
collection = bpy.data.collections.get(collection_name)
assert collection is not None, f"Missing expected collection: {collection_name}"
mesh_objects = [o for o in collection.objects if o.type == "MESH"]
local = []
for obj in mesh_objects:
    for vertex in obj.data.vertices:
        p = obj.matrix_world @ vertex.co
        local.append(tuple(p))
mins = [min(p[i] for p in local) for i in range(3)]
maxs = [max(p[i] for p in local) for i in range(3)]
objects_without_materials = [o.name for o in mesh_objects if not o.data.materials]
external_images = [i.filepath for i in bpy.data.images if i.source == "FILE" and not i.packed_file]
inspection = {
    "status": "PASS",
    "fresh_open": True,
    "asset": str(asset),
    "asset_sha256": hashlib.sha256(asset.read_bytes()).hexdigest().upper(),
    "blender_version": bpy.app.version_string,
    "scene": bpy.context.scene.name,
    "collection": collection_name,
    "collection_object_count": len(collection.objects),
    "mesh_count": len(mesh_objects),
    "nonmesh_types": {kind: sum(o.type == kind for o in collection.objects)
                       for kind in sorted({o.type for o in collection.objects}) if kind != "MESH"},
    "vertex_count": sum(len(o.data.vertices) for o in mesh_objects),
    "polygon_count": sum(len(o.data.polygons) for o in mesh_objects),
    "modifier_count": sum(len(o.modifiers) for o in mesh_objects),
    "linked_library_count": sum(o.library is not None for o in collection.objects),
    "objects_without_materials": objects_without_materials,
    "unpacked_external_images": external_images,
    "world_bounds_m": {"min": mins, "max": maxs},
    "floor_height_and_roof_status": "3 facade levels follow architect renovation elevation; vertical bands are estimates; roof is schematic.",
    "checks": {
        "expected_collection_present": True,
        "all_collection_objects_are_meshes": len(mesh_objects) == len(collection.objects),
        "all_meshes_have_materials": not objects_without_materials,
        "no_external_image_dependencies": not external_images,
        "no_linked_libraries": all(o.library is None for o in collection.objects),
        "no_modifiers": all(not o.modifiers for o in mesh_objects),
    }
}
assert all(inspection["checks"].values()), inspection
out.write_text(json.dumps(inspection, indent=2), encoding="utf-8")
print(json.dumps(inspection, indent=2))
