"""Produce balanced exterior and source-dimension room-vignette reviews."""
import bpy
from mathutils import Vector

BLEND = r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\owen_hall.blend"
ROOT = r"C:\Users\Tobin\Documents\Blender\PurdueMap\audit\owen_hall_independent_grade"
bpy.ops.wm.open_mainfile(filepath=BLEND)
scene = bpy.context.scene

scene.render.resolution_x = 1600
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.exposure = -0.7
scene.view_settings.gamma = 1.0
if "AgX" in {i.identifier for i in scene.view_settings.bl_rna.properties["view_transform"].enum_items}:
    scene.view_settings.view_transform = "AgX"
looks = {i.identifier for i in scene.view_settings.bl_rna.properties["look"].enum_items}
for candidate in ("AgX - Medium High Contrast", "Medium High Contrast"):
    if candidate in looks:
        scene.view_settings.look = candidate
        break

camera_data = bpy.data.cameras.new("Owen_R2_Exterior_Review_Camera")
camera = bpy.data.objects.new("Owen_R2_Exterior_Review_Camera", camera_data)
scene.collection.objects.link(camera)
camera_data.type = "ORTHO"
camera_data.ortho_scale = 126.0
camera.location = (116.0, -18.0, 44.0)
target = Vector((-2.5, 1.5, 8.0))
camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
scene.camera = camera
scene.render.filepath = ROOT + r"\owen_hall_facade.png"
bpy.ops.render.render(write_still=True)

# A separate room crop avoids presenting a typical furnished room as a complete
# or verified as-built floor plan.
for obj in bpy.data.objects:
    obj.hide_render = not (obj.name.startswith(("Owen_Dorm_Room216_", "Owen_Dorm_", "Owen_R2_StandardRoom_", "Owen_R2_Room_")))
scene.view_settings.exposure = -1.3
room_camera_data = bpy.data.cameras.new("Owen_R2_Room_Review_Camera")
room_camera = bpy.data.objects.new("Owen_R2_Room_Review_Camera", room_camera_data)
scene.collection.objects.link(room_camera)
room_camera_data.lens = 50.0
room_camera.location = (-45.5, -38.5, 5.2)
room_target = Vector((-36.7, -34.5, 1.05))
room_camera_data.lens = 42.0
room_camera.rotation_euler = (room_target - room_camera.location).to_track_quat("-Z", "Y").to_euler()
scene.camera = room_camera
scene.render.resolution_x = 1200
scene.render.resolution_y = 850
scene.render.filepath = ROOT + r"\owen_hall_standard_room_vignette.png"
bpy.ops.render.render(write_still=True)
print("Saved exterior and standard-room review renders")
