"""
Render Hovde Hall of Administration (HOVD) Inspection Cameras
Outputs 5 high-resolution PNG renders directly into the brain artifact directory.
"""

import bpy
import os

artifact_dir = r"C:\Users\Tobin\.gemini\antigravity\brain\7d054314-203a-4c1a-bb2d-ad8b0fc54e25"

cams = [
    ("Cam_77_Hovde_South_Hero", "hovde_cam77_south_hero.png"),
    ("Cam_78_Hovde_President_Office_Interior", "hovde_cam78_president_office.png"),
    ("Cam_79_Hovde_BoardOfTrustees_Interior", "hovde_cam79_boardroom.png"),
    ("Cam_80_Hovde_ArtDeco_Rotunda_Interior", "hovde_cam80_rotunda.png"),
    ("Cam_81_Hovde_Mall_Centennial_Aerial", "hovde_cam81_precinct_aerial.png")
]

scene = bpy.context.scene
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

print("=== Starting Hovde Hall Camera Renders ===")
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

print("=== All Hovde Hall Renders Completed! ===")
