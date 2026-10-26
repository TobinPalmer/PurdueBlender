import bpy
import os
from mathutils import Vector

folder = os.path.dirname(__file__)
obj = bpy.data.objects.get("Riverside Covenannt Church")
if obj is None:
    raise RuntimeError("Riverside object is missing")
scene = bpy.context.scene
for name in ("Riverside_Preview_Camera", "Riverside_Preview_Area"):
    datablock = bpy.data.objects.get(name)
    if datablock:
        bpy.data.objects.remove(datablock, do_unlink=True)

points = [obj.matrix_world @ v.co for v in obj.data.vertices]
center = Vector((sum(p.x for p in points)/len(points), sum(p.y for p in points)/len(points), 4.0))
camera_data = bpy.data.cameras.new("Riverside_Preview_Camera")
camera = bpy.data.objects.new("Riverside_Preview_Camera", camera_data)
scene.collection.objects.link(camera)
camera.location = center + Vector((-42.0, -37.0, 28.0))
camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
camera_data.type = "ORTHO"
camera_data.ortho_scale = 51.0
scene.camera = camera

light_data = bpy.data.lights.new("Riverside_Preview_Area", "AREA")
light = bpy.data.objects.new("Riverside_Preview_Area", light_data)
scene.collection.objects.link(light)
light.location = center + Vector((-24.0, -18.0, 34.0))
light.rotation_euler = (center - light.location).to_track_quat("-Z", "Y").to_euler()
light_data.energy = 900
light_data.shape = "DISK"
light_data.size = 24.0

scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1200
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.filepath = os.path.join(folder, "preview_detail_r3.png")
scene.view_settings.view_transform = "AgX"
scene.view_settings.exposure = -0.6
scene.world.color = (0.035, 0.045, 0.06)
bpy.ops.render.render(write_still=True)
print("RENDERED=" + scene.render.filepath)

# Straight-on south entrance view and campus-axis top view complement the oblique preview.
camera.location = center + Vector((0.0, -52.0, 8.5))
camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
camera_data.ortho_scale = 40.0
light.location = center + Vector((-10.0, -25.0, 24.0))
light.rotation_euler = (center - light.location).to_track_quat("-Z", "Y").to_euler()
scene.render.filepath = os.path.join(folder, "preview_front_r1.png")
bpy.ops.render.render(write_still=True)
print("RENDERED=" + scene.render.filepath)

camera.location = center + Vector((0.0, 0.0, 58.0))
camera.rotation_euler = (0.0, 0.0, 0.0)
camera_data.ortho_scale = 40.0
light.location = center + Vector((-18.0, -12.0, 35.0))
light.rotation_euler = (center - light.location).to_track_quat("-Z", "Y").to_euler()
scene.render.filepath = os.path.join(folder, "preview_top_r1.png")
bpy.ops.render.render(write_still=True)
print("RENDERED=" + scene.render.filepath)
