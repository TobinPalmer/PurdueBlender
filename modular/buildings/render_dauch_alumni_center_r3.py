"""Render Dauch R3 overview, roof, and sign previews from saved asset."""
import bpy
import os
from mathutils import Vector
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "audit", "dauch_alumni_center")
os.makedirs(OUT, exist_ok=True)
scene = bpy.context.scene
old_camera = scene.camera
old_engine = scene.render.engine
old_res = (scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage)
old_filepath = scene.render.filepath
cam_data = bpy.data.cameras.new("DAUC_r3_audit_camera_data")
cam = bpy.data.objects.new("DAUC_r3_audit_camera", cam_data)
scene.collection.objects.link(cam)
cam.data.type = "ORTHO"
lights = []
for name, loc, power, size in (("DAUC_r3_audit_key", (8, -34, 45), 5200, 28), ("DAUC_r3_audit_fill", (-32, -6, 24), 2500, 24)):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = power
    data.shape = "DISK"
    data.size = size
    light = bpy.data.objects.new(name, data)
    scene.collection.objects.link(light)
    light.location = loc
    light.rotation_euler = (Vector((0, -5, 5)) - light.location).to_track_quat("-Z", "Y").to_euler()
    lights.append(light)
scene.render.engine = "CYCLES"
scene.cycles.samples = 32
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.camera = cam

def look_at(location, target):
    cam.location = location
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()

scene.render.resolution_x, scene.render.resolution_y = 1280, 900
cam.data.ortho_scale = 84
look_at((55, -74, 36), (0, -1, 7.5))
scene.render.filepath = os.path.join(OUT, "dauch_alumni_center_r3_overview.png")
bpy.ops.render.render(write_still=True)

scene.render.resolution_x, scene.render.resolution_y = 1280, 900
cam.data.ortho_scale = 74
# Low, nearly level south view makes the shallow curved roof silhouette legible.
look_at((4, -78, 23), (0, -8, 13.8))
scene.render.filepath = os.path.join(OUT, "dauch_alumni_center_r3_roof_profile.png")
bpy.ops.render.render(write_still=True)

scene.render.resolution_x, scene.render.resolution_y = 1100, 760
cam.data.ortho_scale = 9.0
look_at((18.5, -34.1, 5), (13.7, -24.6, 1.1))
scene.render.filepath = os.path.join(OUT, "dauch_alumni_center_r3_sign_detail.png")
bpy.ops.render.render(write_still=True)

scene.camera = old_camera
scene.render.engine = old_engine
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = old_res
scene.render.filepath = old_filepath
for obj in [cam, *lights]:
    bpy.data.objects.remove(obj, do_unlink=True)
bpy.data.cameras.remove(cam_data)
print("DAUC_R3_PREVIEWS", OUT)
