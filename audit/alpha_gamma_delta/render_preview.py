import bpy
import os
from mathutils import Vector

folder = os.path.dirname(__file__)
collection = bpy.data.collections.get("Asset_massing_house_301841608_d56a4c4")
if collection is None or len(collection.objects) != 1:
    raise RuntimeError("Alpha Gamma Delta collection is missing or malformed")
obj = collection.objects[0]
points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
low = Vector(tuple(min(point[i] for point in points) for i in range(3)))
high = Vector(tuple(max(point[i] for point in points) for i in range(3)))
center = (low+high)*0.5
span = max(high.x-low.x, high.y-low.y, high.z-low.z)
scene = bpy.context.scene
camera_data = bpy.data.cameras.new("AGD_Preview_Camera")
camera = bpy.data.objects.new("AGD_Preview_Camera", camera_data)
scene.collection.objects.link(camera)
camera.location = center+Vector((-span*1.25,-span*1.35,span*0.52))
camera.rotation_euler = (center-camera.location).to_track_quat("-Z","Y").to_euler()
camera_data.type = "ORTHO"
camera_data.ortho_scale = span*1.65
scene.camera = camera
light_data = bpy.data.lights.new("AGD_Preview_Area", "AREA")
light = bpy.data.objects.new("AGD_Preview_Area", light_data)
scene.collection.objects.link(light)
light.location = center+Vector((-span, -span*0.8, span*1.8))
light.rotation_euler = (center-light.location).to_track_quat("-Z","Y").to_euler()
light_data.energy = span*span*0.42
light_data.shape = "DISK"
light_data.size = span*0.8
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1120
scene.render.resolution_y = 840
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = os.path.join(folder,"preview_detail.png")
scene.world.color = (0.035,0.035,0.035)
scene.view_settings.view_transform = "AgX"
scene.view_settings.exposure = -0.25
bpy.ops.render.render(write_still=True)
print("RENDERED="+scene.render.filepath)
