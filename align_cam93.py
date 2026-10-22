import bpy
import math
import os

blend_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
output_dir = r"C:\Users\Tobin\.gemini\antigravity\brain\7d054314-203a-4c1a-bb2d-ad8b0fc54e25"

bpy.ops.wm.open_mainfile(filepath=blend_path)

cam93 = bpy.data.objects.get("Cam_93_MATH_175_LectureHall_Interior")
if cam93:
    # Aisle position: local X = -5.0 + 2.0 = -3.0 (world X = -183.62)
    # Y = -135.0 (world Y), Z = 3.2m elevated above tiers looking down aisle
    cam93.location = (-183.62, -135.5, 3.2)
    cam93.rotation_euler = (math.radians(102), 0, math.radians(180))
    cam93.data.lens = 19.0

bpy.ops.wm.save_mainfile(filepath=blend_path)
print("Cam 93 aisle alignment saved!")

scene = bpy.context.scene
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.camera = cam93
scene.render.filepath = os.path.join(output_dir, "math_cam93_lecturehall_175.png")
bpy.ops.render.render(write_still=True)
print("Re-rendered Cam 93 successfully!")
