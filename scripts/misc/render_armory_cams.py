"""
Render Purdue Armory (AR - 1918) Inspection Cameras
Outputs 5 high-resolution PNG renders directly into the brain artifact directory.
"""

import bpy
import os

artifact_dir = r"C:\Users\Tobin\.gemini\antigravity\brain\7d054314-203a-4c1a-bb2d-ad8b0fc54e25"

cams = [
    ("Cam_87_Armory_UniversitySt_Hero", "armory_cam87_universityst_hero.png"),
    ("Cam_88_Armory_DrillHall_Colossal_Trusses_Interior", "armory_cam88_drillhall_trusses.png"),
    ("Cam_89_Armory_OfficersClub_Lounge_Interior", "armory_cam89_officersclub_lounge.png"),
    ("Cam_90_Armory_Mezzanine_Overlook_Interior", "armory_cam90_mezzanine_overlook.png"),
    ("Cam_91_Armory_Precinct_Aerial", "armory_cam91_precinct_aerial.png")
]

scene = bpy.context.scene
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

print("=== Starting Purdue Armory Camera Renders ===")
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

print("=== All Purdue Armory Renders Completed! ===")
