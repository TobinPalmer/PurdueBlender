"""Create a cutaway audit view of the estimated Maclure ground-floor interior.

This loads the delivered library in a fresh Blender process and writes only a
preview image; it does not save changes to the asset.
"""
import bpy
import math
from pathlib import Path
from mathutils import Vector

root = Path(__file__).resolve().parents[2]
asset_path = root / "modular" / "buildings" / "maclure_cooperative.blend"
out_path = Path(__file__).resolve().parent / "maclure_interior_preview.png"
bpy.ops.wm.open_mainfile(filepath=str(asset_path))
scene = bpy.context.scene
interior_terms = (
    "Estimated interior floor slab", "Estimated room partition",
    "Formal living room", "Communal dining", "Dining chair",
)
asset_col = bpy.data.collections.get("Asset_maclure_cooperative")
assert asset_col is not None
for obj in asset_col.objects:
    obj.hide_render = not any(term in obj.name for term in interior_terms)
    if "Estimated interior floor slab" in obj.name and obj.location.z > 1.0:
        obj.hide_render = True
camera_data = bpy.data.cameras.new("Estimated interior plan camera")
camera = bpy.data.objects.new("Estimated interior plan camera", camera_data)
scene.collection.objects.link(camera)
camera.location = (-0.3, 2.2, 18)
target = Vector((-0.3, 2.2, 0.2))
camera.rotation_euler = (target - Vector(camera.location)).to_track_quat("-Z", "Y").to_euler()
camera.data.type = "ORTHO"
camera.data.ortho_scale = 19
scene.camera = camera
key_data = bpy.data.lights.new("Interior audit softbox", "AREA")
key = bpy.data.objects.new("Interior audit softbox", key_data)
scene.collection.objects.link(key)
key.location = (0, 2, 13)
key.data.energy = 9000
key.data.shape = "DISK"
key.data.size = 10
scene.render.resolution_x = 1100
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.filepath = str(out_path)
bpy.ops.render.render(write_still=True)
print("Fresh-open interior preview:", out_path)
