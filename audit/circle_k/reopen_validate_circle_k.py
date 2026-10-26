"""Read-only structural check for the saved Circle K asset."""
import bpy
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
asset_id = "massing_circle_k_fa39c23"
collection_name = "Asset_" + asset_id
scene_name = "Building_" + asset_id
collection = bpy.data.collections.get(collection_name)
scene = bpy.data.scenes.get(scene_name)
assert collection is not None, "expected asset collection missing"
assert scene is not None, "expected scene missing"
assert collection in list(scene.collection.children), "asset collection is not a direct scene child"
assert bpy.context.scene.name == scene_name, "expected building scene was not active on open"

depsgraph = bpy.context.evaluated_depsgraph_get()
all_points = []
entries = []
for obj in collection.objects:
    evaluated = obj.evaluated_get(depsgraph)
    bb = [evaluated.matrix_world @ __import__("mathutils").Vector(corner) for corner in evaluated.bound_box]
    all_points.extend(bb)
    mesh = evaluated.to_mesh()
    nverts = len(mesh.vertices) if mesh else 0
    if mesh:
        evaluated.to_mesh_clear()
    entries.append({
        "name": obj.name,
        "type": obj.type,
        "dimensions_m": [round(float(v), 4) for v in obj.dimensions],
        "evaluated_vertices": nverts,
        "modifiers": [m.name for m in obj.modifiers],
        "library": obj.library.filepath if obj.library else None,
    })

bounds = [[round(min(p[i] for p in all_points), 4), round(max(p[i] for p in all_points), 4)] for i in range(3)]
result = {
    "asset_id": asset_id,
    "blend_file": str(bpy.data.filepath),
    "reopened_with_blender": bpy.app.version_string,
    "scene": scene.name,
    "asset_collection": collection.name,
    "collection_is_direct_scene_child": True,
    "object_count": len(collection.objects),
    "object_types": {t: sum(1 for obj in collection.objects if obj.type == t) for t in sorted({obj.type for obj in collection.objects})},
    "world_bounds_m": bounds,
    "store_shell_bounds_m": next((entry["dimensions_m"] for entry in entries if entry["name"] == "Circle K"), None),
    "asset_objects": entries,
    "external_absolute_asset_links": [entry for entry in entries if entry["library"] and (":" in entry["library"] or entry["library"].startswith("/"))],
    "result": "PASS" if all(e["evaluated_vertices"] > 0 for e in entries) else "FAIL",
}
out = root / "audit" / "circle_k" / "reopen_validation_2026-10-26.json"
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print("CIRCLE_K_REOPEN_VALIDATION", json.dumps({k: result[k] for k in ("result", "object_count", "object_types", "world_bounds_m", "store_shell_bounds_m")}, indent=2))
