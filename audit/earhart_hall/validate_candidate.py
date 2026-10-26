"""Fresh-open validation and entry view render for the Earhart Hall asset."""
import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Vector

root = Path(__file__).resolve().parents[2]
asset_path = root / "modular/buildings/massing_earhart_hall_0f14209.blend"
audit = root / "audit/earhart_hall"
assert bpy.data.filepath.lower() == str(asset_path).lower(), bpy.data.filepath
scene = bpy.data.scenes.get("Building_massing_earhart_hall_0f14209")
collection = bpy.data.collections.get("Asset_massing_earhart_hall_0f14209")
assert scene is not None and collection is not None
assert collection.name in {c.name for c in scene.collection.children}
assert len(collection.objects) >= 20
assert any("Standard_Room" in o.name for o in collection.objects)
assert any("Dining_Court" in o.name for o in collection.objects)
assert all(not image.filepath or image.packed_file for image in bpy.data.images)

verts = [obj.matrix_world @ v.co for obj in collection.objects if obj.type == "MESH" for v in obj.data.vertices]
bounds = [[min(v[i] for v in verts), max(v[i] for v in verts)] for i in range(3)]
assert -1000 < bounds[0][0] < -995 and -914 < bounds[0][1] < -908
assert -212 < bounds[1][0] < -207 and -142 < bounds[1][1] < -136
assert 24 < bounds[2][1] < 27

# Render a second, fresh-open view of the documented dining court entry.
preview = bpy.data.collections.get("Preview_only_context_exclude_from_master")
camera = next(o for o in preview.objects if o.type == "CAMERA")
scene.camera = camera
camera.data.type = "ORTHO"
camera.data.ortho_scale = 40
camera.location = (-951.5, -284.0, 13.5)
target = Vector((-951.5, -198.3, 5.0))
camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
scene.render.resolution_x = 1280
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.filepath = str(audit / "dining_court_entry_preview.png")
bpy.ops.render.render(write_still=True)

report = {
    "fresh_open": True,
    "asset_path": str(asset_path),
    "scene": scene.name,
    "asset_collection": collection.name,
    "asset_object_count": len(collection.objects),
    "mesh_object_count": sum(o.type == "MESH" for o in collection.objects),
    "material_count": len(bpy.data.materials),
    "external_image_dependencies": [i.filepath for i in bpy.data.images if i.filepath and not i.packed_file],
    "geometry_bounds_world_m": bounds,
    "blend_sha256": hashlib.sha256(asset_path.read_bytes()).hexdigest(),
    "validation": "passed",
}
(audit / "fresh_open_validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print("ERHT_FRESH_OPEN_VALIDATION", json.dumps(report))
