"""
Render inspection and comparison views for Krannert Building (KRAN)
"""

import bpy
import os

BLEND_FILE = os.path.abspath("modular/buildings/krannert_building.blend")
OUT_DIR = os.path.abspath("modular/buildings/krannert_building_evidence")
os.makedirs(OUT_DIR, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)
scene = bpy.context.scene

# Render settings
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100

cameras = [
    "Cam_KRAN_01_Ortho_Footprint_Top",
    "Cam_KRAN_02_SW_StateSt_Entrance",
    "Cam_KRAN_03_SE_GrantSt_Corner",
    "Cam_KRAN_04_East_Skywalk_Dock",
    "Cam_KRAN_05_North_Auditorium_Wing",
    "Cam_KRAN_06_West_Facade_Clock",
]

for cam_name in cameras:
    cam_obj = bpy.data.objects.get(cam_name)
    if not cam_obj:
        print(f"Warning: camera {cam_name} not found")
        continue
    scene.camera = cam_obj
    out_path = os.path.join(OUT_DIR, f"{cam_name}.png")
    scene.render.filepath = out_path
    print(f"Rendering {cam_name} to {out_path}...")
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {out_path}")

print("=== ALL RENDERS COMPLETED ===")
