"""
Render Class of 1950 Lecture Hall (CL50) Inspection Cameras
Outputs 5 high-resolution PNG renders directly into the brain artifact directory.
"""

import bpy
import os

artifact_dir = r"C:\Users\Tobin\.gemini\antigravity\brain\7d054314-203a-4c1a-bb2d-ad8b0fc54e25"

cams = [
    ("Cam_82_CL50_OvalDrive_Hero", "cl50_cam82_ovaldrive_hero.png"),
    ("Cam_83_CL50_224_Auditorium_Interior", "cl50_cam83_auditorium_224.png"),
    ("Cam_84_CL50_EinsteinBagels_Atrium_Interior", "cl50_cam84_einstein_atrium.png"),
    ("Cam_85_CL50_Stage_Instructor_Interior", "cl50_cam85_stage_instructor.png"),
    ("Cam_86_CL50_MemorialMall_Precinct_Aerial", "cl50_cam86_precinct_aerial.png")
]

scene = bpy.context.scene
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

print("=== Starting CL50 Camera Renders ===")
for cam_name, fname in cams:
    cam_obj = bpy.data.objects.get(cam_name)
    if cam_obj:
        scene.camera = cam_obj
        out_path = os.path.join(artifact_dir, fname)
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        size_kb = os.path.getsize(out_path) / 1024
        print(f"Rendered {cam_name} -> {fname} ({size_kb:.1f} KB)")
    else:
        print(f"ERROR: Camera {cam_name} not found!")

print("=== All CL50 Renders Completed! ===")
