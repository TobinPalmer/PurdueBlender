"""
Render Stewart Center (STEW) Inspection Cameras
Outputs 5 high-resolution PNG renders directly into the brain artifact directory.
"""

import bpy
import os

artifact_dir = r"C:\Users\Tobin\.gemini\antigravity\brain\7d054314-203a-4c1a-bb2d-ad8b0fc54e25"

cams = [
    ("Cam_72_Stewart_South_Hero", "stewart_cam72_south_hero.png"),
    ("Cam_73_Stewart_LoebPlayhouse_Interior", "stewart_cam73_loeb_playhouse.png"),
    ("Cam_74_Stewart_HSSE_Library_Interior", "stewart_cam74_hsse_library.png"),
    ("Cam_75_Stewart_RingelGallery_Interior", "stewart_cam75_ringel_gallery.png"),
    ("Cam_76_Stewart_North_Aerial", "stewart_cam76_precinct_aerial.png")
]

scene = bpy.context.scene
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

print("=== Starting Stewart Center Camera Renders ===")
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

print("=== All Stewart Center Renders Completed! ===")
