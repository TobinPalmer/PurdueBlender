import bpy
import os
from mathutils import Vector

folder = os.path.dirname(__file__)
obj = bpy.data.objects.get("Shreve Hall")
if obj is None:
    raise RuntimeError("Shreve object is missing")
scene = bpy.context.scene
for name in ("Shreve_Preview_Camera", "Shreve_Preview_Area"):
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
coords = [obj.matrix_world @ v.co for v in obj.data.vertices]
target = Vector((min(p.x for p in coords)+3.0, (min(p.y for p in coords)+max(p.y for p in coords))/2.0, 8.0))
camera_data = bpy.data.cameras.new("Shreve_Preview_Camera")
camera = bpy.data.objects.new("Shreve_Preview_Camera", camera_data)
scene.collection.objects.link(camera)
camera.location = target + Vector((-34.0, -24.0, 19.0))
camera.rotation_euler = (target-camera.location).to_track_quat("-Z", "Y").to_euler()
camera_data.type = "ORTHO"
camera_data.ortho_scale = 33.0
scene.camera = camera
light_data = bpy.data.lights.new("Shreve_Preview_Area", "AREA")
light = bpy.data.objects.new("Shreve_Preview_Area", light_data)
scene.collection.objects.link(light)
light.location = target + Vector((-24.0, -15.0, 28.0))
light.rotation_euler = (target-light.location).to_track_quat("-Z", "Y").to_euler()
light_data.energy = 350
light_data.shape = "DISK"
light_data.size = 22.0
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1200
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = os.path.join(folder, "preview_detail_r2.png")
scene.view_settings.view_transform = "AgX"
scene.view_settings.exposure = -0.50
scene.world.color = (0.035, 0.045, 0.06)
bpy.ops.render.render(write_still=True)
print("RENDERED=" + scene.render.filepath)
