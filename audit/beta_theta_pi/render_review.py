"""Render fixed review views from the saved Beta Theta Pi library."""
import bpy
import math
from mathutils import Vector

scene = bpy.context.scene
camera_data = bpy.data.cameras.new("BetaThetaPi_review_camera")
camera = bpy.data.objects.new("BetaThetaPi_review_camera", camera_data)
scene.collection.objects.link(camera)
camera_data.type = "ORTHO"
camera_data.ortho_scale = 56
scene.camera = camera
light_data = bpy.data.lights.new("BetaThetaPi_review_sun", "SUN")
light = bpy.data.objects.new("BetaThetaPi_review_sun", light_data)
scene.collection.objects.link(light)
light.rotation_euler = (math.radians(20), math.radians(-20), math.radians(-25))
light_data.energy = 3.0
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 900
scene.render.resolution_y = 700
scene.render.resolution_percentage = 100
scene.world.color = (0.28, 0.31, 0.37)
target = Vector((816, -396, 4.5))
poses = {
    "west": (767, -396, 7.5),
    "east": (866, -396, 7.5),
    "close": (778, -396, 7.5),
    "south": (816, -452, 25),
    "north": (816, -340, 25),
    "aerial": (816, -396, 80),
}
for name, position in poses.items():
    camera.location = position
    camera.rotation_euler = (target - Vector(position)).to_track_quat("-Z", "Y").to_euler()
    camera_data.ortho_scale = 28 if name == "close" else (52 if name == "aerial" else 56)
    scene.render.filepath = f"//../../audit/beta_theta_pi/preview_r4_{name}.png"
    bpy.ops.render.render(write_still=True)
