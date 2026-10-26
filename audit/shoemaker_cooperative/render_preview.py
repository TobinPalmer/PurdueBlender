import bpy
import json
import math
import os
from mathutils import Vector

folder = os.path.dirname(__file__)
obj = bpy.data.objects.get("Shoemaker Cooperative")
if obj is None:
    raise RuntimeError("Shoemaker object is missing")
scene = bpy.context.scene
for name in ("Shoemaker_Preview_Camera", "Shoemaker_Preview_Area"):
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
points = [obj.matrix_world @ v.co for v in obj.data.vertices]
center = Vector((sum(p.x for p in points)/len(points), sum(p.y for p in points)/len(points), 4.8))
camera_data = bpy.data.cameras.new("Shoemaker_Preview_Camera")
camera = bpy.data.objects.new("Shoemaker_Preview_Camera", camera_data)
scene.collection.objects.link(camera)
camera.location = center + Vector((-40.0, -20.0, 19.0))
camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
camera_data.type = "ORTHO"
camera_data.ortho_scale = 42.0
scene.camera = camera
light_data = bpy.data.lights.new("Shoemaker_Preview_Area", "AREA")
light = bpy.data.objects.new("Shoemaker_Preview_Area", light_data)
scene.collection.objects.link(light)
light.location = center + Vector((-24.0, -20.0, 35.0))
light.rotation_euler = (center - light.location).to_track_quat("-Z", "Y").to_euler()
light_data.energy = 1200
light_data.shape = "DISK"
light_data.size = 26
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1200
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = os.path.join(folder, "preview_detail_r2.png")
scene.view_settings.view_transform = "AgX"
scene.view_settings.exposure = -0.3
scene.world.color = (0.035, 0.045, 0.06)
bpy.ops.render.render(write_still=True)
print("RENDERED=" + scene.render.filepath)
