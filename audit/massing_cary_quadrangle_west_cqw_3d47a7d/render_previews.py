"""Refresh the CQW evidence renders from the saved asset using bright daylight."""
import bpy
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular" / "buildings" / "massing_cary_quadrangle_west_cqw_3d47a7d.blend"
EVIDENCE = ROOT / "audit" / "massing_cary_quadrangle_west_cqw_3d47a7d"
bpy.context.preferences.filepaths.save_version = 0
scene = bpy.context.scene
if scene.name != "Building_massing_cary_quadrangle_west_cqw_3d47a7d":
    raise RuntimeError("Wrong CQW scene opened")
preview = bpy.data.collections.get("CQW_Preview_Only")
if preview is None:
    preview = bpy.data.collections.new("CQW_Preview_Only")
    scene.collection.children.link(preview)
for name, energy in (("CQW key", 32000.0), ("CQW fill", 16000.0)):
    light = bpy.data.objects.get(name)
    if light is not None:
        light.data.energy = energy
for obj in bpy.data.objects:
    if "pointed arch arm" in obj.name:
        side = -1 if obj.name.endswith("-1") else 1
        obj.rotation_euler[0] = -side * 0.72
if bpy.data.objects.get("CQW broad daylight") is None:
    data = bpy.data.lights.new("CQW broad daylight", "SUN")
    sun = bpy.data.objects.new("CQW broad daylight", data)
    preview.objects.link(sun)
    sun.location = (0, 0, 50)
    sun.rotation_euler = (Vector((0, 0, 0)) - Vector(sun.location)).to_track_quat("-Z", "Y").to_euler()
else:
    sun = bpy.data.objects["CQW broad daylight"]
sun.data.energy = 6.0
sun.data.angle = math.radians(18.0)
scene.world.use_nodes = True
background = scene.world.node_tree.nodes.get("Background")
background.inputs["Color"].default_value = (0.55, 0.55, 0.55, 1.0)
background.inputs["Strength"].default_value = 0.8
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.eevee.taa_render_samples = 8
scene.render.resolution_x = 1280
scene.render.resolution_y = 800
scene.render.resolution_percentage = 80
scene.render.image_settings.file_format = "PNG"
camera = bpy.data.objects.get("CQW evidence camera")
if camera is None:
    raise RuntimeError("Evidence camera is missing")
scene.camera = camera
camera.location = (-330.0, 540.0, 38.0)
camera.data.type = "ORTHO"
camera.data.ortho_scale = 105.0
camera.rotation_euler = (Vector((-447.0, 556.8, 8.5)) - Vector(camera.location)).to_track_quat("-Z", "Y").to_euler()
scene.render.filepath = str(EVIDENCE / "preview_cqw_east_court.png")
bpy.ops.render.render(write_still=True)
camera.location = (-330.0, 552.8, 16.0)
camera.data.ortho_scale = 52.0
camera.rotation_euler = (Vector((-439.4, 556.8, 8.5)) - Vector(camera.location)).to_track_quat("-Z", "Y").to_euler()
scene.render.filepath = str(EVIDENCE / "preview_cqw_entrance.png")
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print("Saved bright CQW preview renders and camera/light state.")
