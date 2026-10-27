import bpy
from pathlib import Path
from mathutils import Vector

root = Path(__file__).resolve().parents[2]
asset = root / "modular/buildings/massing_veterinary_animal_isolation_building_2_ebb4142.blend"
out = Path(__file__).resolve().parent / "preview_interior_cutaway.png"
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene = bpy.context.scene
collection = bpy.data.collections.get("Asset_massing_veterinary_animal_isolation_building_2_ebb4142")
for obj in collection.objects:
    if obj.name.startswith(("VA2 flat roof", "VA2 roof perimeter", "VA2 central rooftop",
                            "VA2 low rooftop", "VA2 rooftop HVAC", "VA2 roof exhaust",
                            "VA2 roof access", "VA2 east exterior window", "VA2 west exterior window",
                            "VA2 east staff access", "VA2 west staff access")):
        obj.hide_render = True
    if obj.name.startswith(("VA2 exterior east", "VA2 exterior west")) and any(
        token in obj.name for token in (" wall panel", " concrete base", " structural interstitial", " roof fascia", " HVAC louver", " HVAC horizontal louver", " upper interstitial panel")):
        obj.hide_render = True
camera_data = bpy.data.cameras.new("VA2 interior explanatory camera")
camera = bpy.data.objects.new("VA2 interior explanatory camera", camera_data)
scene.collection.objects.link(camera)
camera.location = (12.0, -5.0, 3.6)
camera.data.lens = 40
camera.rotation_euler = (Vector((0.0, 0.0, 1.5)) - camera.location).to_track_quat("-Z", "Y").to_euler()
scene.camera = camera
scene.render.filepath = str(out)
bpy.ops.render.render(write_still=True)
