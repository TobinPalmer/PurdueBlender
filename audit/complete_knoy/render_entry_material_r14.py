"""Render saved Knoy source entrance materials without saving scene changes."""
import bpy
from pathlib import Path
from mathutils import Vector

ROOT = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
BLEND = ROOT / "modular" / "buildings" / "knoy_hall.blend"
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
scene = bpy.context.scene
camd = bpy.data.cameras.new("R14_Entry_Material_Camera")
cam = bpy.data.objects.new("R14_Entry_Material_Camera", camd)
scene.collection.objects.link(cam)
cam.location = (8.0, -55.4, 7.0)
target = Vector((0.76, -46.34, 4.25))
cam.rotation_euler = (target - Vector(cam.location)).to_track_quat("-Z", "Y").to_euler()
camd.lens = 52
scene.camera = cam
for name, location, power, size in (
    ("Key", (-1.5, -52, 9.5), 2800, 7),
    ("Fill", (6, -50, 3.5), 800, 5),
):
    ld = bpy.data.lights.new(f"R14_Entry_Material_{name}", "AREA")
    lo = bpy.data.objects.new(f"R14_Entry_Material_{name}", ld)
    scene.collection.objects.link(lo)
    lo.location = location
    ld.energy = power
    ld.shape = "DISK"
    ld.size = size
    lo.rotation_euler = (target - Vector(location)).to_track_quat("-Z", "Y").to_euler()
if scene.world:
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.36, 0.42, 0.52, 1)
    bg.inputs["Strength"].default_value = 0.28
scene.render.engine = "CYCLES"
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.resolution_x = 1700
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.view_settings.view_transform = "AgX"
out = ROOT / "audit" / "complete_knoy" / "knoy_entrance_detail_material_r14.png"
scene.render.filepath = str(out)
bpy.ops.render.render(write_still=True)
print("R14_RENDER", out, "saved asset reopened; render-only camera and lights not saved")
