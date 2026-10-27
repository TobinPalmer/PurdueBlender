"""Fresh-open validation for the Beta Sigma Psi library asset."""
import bpy
import json
import math
from pathlib import Path

root = Path(bpy.data.filepath).resolve().parents[2]
asset_id = "massing_house_301841254_29ab02d"
collection_name = f"Asset_{asset_id}"
collection = bpy.data.collections.get(collection_name)
if collection is None:
    raise RuntimeError(f"Missing expected exported collection {collection_name}")
objects = list(collection.objects)
if len(objects) != 1 or objects[0].name != "House_301841254" or objects[0].type != "MESH":
    raise RuntimeError(f"Unexpected exported collection contents: {[o.name for o in objects]}")
obj = objects[0]
depsgraph = bpy.context.evaluated_depsgraph_get()
eval_obj = obj.evaluated_get(depsgraph)
eval_mesh = eval_obj.to_mesh()
verts = [obj.matrix_world @ v.co for v in eval_mesh.vertices]
bounds = [[min(v[i] for v in verts), max(v[i] for v in verts)] for i in range(3)]
polys = len(eval_mesh.polygons)
tris = sum(max(1, len(p.vertices)-2) for p in eval_mesh.polygons)
materials = [m.name if m else None for m in eval_mesh.materials]
modifiers = [{"name": m.name, "type": m.type, "show_viewport": m.show_viewport, "show_render": m.show_render} for m in obj.modifiers]
external_images = [im.filepath for im in bpy.data.images if im.source == "FILE"]
result = {
    "reopened_file": str(Path(bpy.data.filepath).resolve()),
    "reopened_successfully": True,
    "asset_id": asset_id,
    "asset_collection": collection_name,
    "collection_transform": "n/a; direct campus-coordinate massing library, exported geometry uses identity object transform",
    "collection_objects": [o.name for o in objects],
    "object_location": list(obj.location),
    "object_rotation_euler_radians": list(obj.rotation_euler),
    "object_scale": list(obj.scale),
    "evaluated_world_bounds_m": bounds,
    "evaluated_vertices": len(eval_mesh.vertices),
    "evaluated_polygons": polys,
    "evaluated_triangle_estimate": tris,
    "material_slots": materials,
    "modifiers": modifiers,
    "external_image_dependencies": external_images,
    "relative_asset_links": [lib.filepath for lib in bpy.data.libraries if lib.filepath],
    "checks": {
        "expected_collection_present": True,
        "single_named_mesh_object": True,
        "identity_object_transform": all(abs(a-b)<1e-6 for a,b in zip((*obj.location,*obj.rotation_euler,*obj.scale),(0,0,0,0,0,0,1,1,1))),
        "positive_height_and_plan_bounds": all(bounds[i][1]>bounds[i][0] for i in range(3)),
        "materials_assigned": bool(materials),
        "no_external_file_images": not external_images,
        "no_modifiers": not modifiers,
    }
}
eval_obj.to_mesh_clear()
out = root / "audit" / "beta_sigma_psi" / "reopen_verification.json"
out.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
print("BETA_SIGMA_PSI_REOPEN="+json.dumps(result))
