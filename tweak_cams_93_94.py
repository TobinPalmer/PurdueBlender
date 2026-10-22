import bpy
import math
import os

blend_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
output_dir = r"C:\Users\Tobin\.gemini\antigravity\brain\7d054314-203a-4c1a-bb2d-ad8b0fc54e25"

bpy.ops.wm.open_mainfile(filepath=blend_path)

cam93 = bpy.data.objects.get("Cam_93_MATH_175_LectureHall_Interior")
if cam93:
    cam93.location = (-185.62, -137.5, 2.3)
    cam93.rotation_euler = (math.radians(92), 0, math.radians(180))
    cam93.data.lens = 18.0

cam94 = bpy.data.objects.get("Cam_94_MATH_Library_Study_Interior")
if cam94:
    cam94.location = (-181.0, -121.5, 12.3)
    cam94.rotation_euler = (math.radians(78), 0, math.radians(15))
    cam94.data.lens = 18.0

bpy.ops.wm.save_mainfile(filepath=blend_path)
print("Cameras 93 and 94 updated successfully!")

scene = bpy.context.scene
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100

for cname, fname in [("Cam_93_MATH_175_LectureHall_Interior", "math_cam93_lecturehall_175.png"), ("Cam_94_MATH_Library_Study_Interior", "math_cam94_library_study.png")]:
    scene.camera = bpy.data.objects.get(cname)
    scene.render.filepath = os.path.join(output_dir, fname)
    bpy.ops.render.render(write_still=True)
    print(f"Re-rendered {cname} successfully!")
