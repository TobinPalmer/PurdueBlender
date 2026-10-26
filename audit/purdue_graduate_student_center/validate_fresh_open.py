"""Fresh-open structural validation for the PGSC modular Blender asset."""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector

root = Path(__file__).resolve().parents[2]
asset_id = "massing_purdue_graduate_student_center_af9c5c7"
blend = root / "modular" / "buildings" / f"{asset_id}.blend"
expected_collection = f"Asset_{asset_id}"
expected_scene = f"Building_{asset_id}"
collection = bpy.data.collections.get(expected_collection)
assert collection is not None, f"Missing {expected_collection}"
assert bpy.context.scene.name == expected_scene, f"Unexpected active scene {bpy.context.scene.name}"
assert collection.get("asset_id") == asset_id
geom = [o for o in collection.all_objects if o.type in {"MESH", "CURVE", "FONT"}]
assert geom, "No geometry in asset collection"
bpy.context.view_layer.update()
bounds = [[min((o.matrix_world @ Vector(c))[i] for o in geom for c in o.bound_box),
           max((o.matrix_world @ Vector(c))[i] for o in geom for c in o.bound_box)] for i in range(3)]
external = sorted(img.filepath for img in bpy.data.images if img.source == "FILE")
materials = sorted({m.name for o in geom for m in o.data.materials if m})
result = {
    "validation": "PASS",
    "fresh_open": True,
    "asset_id": asset_id,
    "blend_path": str(blend.relative_to(root)).replace("\\", "/"),
    "scene": bpy.context.scene.name,
    "collection": collection.name,
    "geometry_object_count": len(geom),
    "material_count_used": len(materials),
    "materials": materials,
    "local_bounds_m": bounds,
    "external_image_paths": external,
    "blend_sha256": hashlib.sha256(blend.read_bytes()).hexdigest(),
}
out = root / "audit" / "purdue_graduate_student_center" / "fresh_open_validation.json"
out.write_text(json.dumps(result, indent=2), encoding="utf-8")
print("PGSC_FRESH_OPEN_VALIDATION=" + json.dumps(result))
