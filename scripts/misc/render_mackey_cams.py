"""
Render 5 Calibrated Inspection Cameras for Mackey Arena (MACK)
==============================================================
"""

import bpy
import os

def render_cams():
    artifact_dir = r"C:\Users\Tobin\.gemini\antigravity\brain\7d054314-203a-4c1a-bb2d-ad8b0fc54e25"
    os.makedirs(artifact_dir, exist_ok=True)
    
    scene = bpy.context.scene
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.engine = 'BLENDER_EEVEE'
    
    cams = [
        ("Cam_62_Mackey_Arena_North_WoodenPlaza_Hero", "mackey_arena_cam62_north_woodenplaza.png"),
        ("Cam_63_Mackey_Arena_KeadyCourt_CenterCourt_Hero", "mackey_arena_cam63_keadycourt_hero.png"),
        ("Cam_64_Mackey_Arena_UpperBowl_CenterHungScoreboard", "mackey_arena_cam64_scoreboard_upperbowl.png"),
        ("Cam_65_Mackey_Arena_Courtside_Hoop_and_Bench", "mackey_arena_cam65_courtside_hoop.png"),
        ("Cam_66_Mackey_Arena_Athletic_Precinct_Aerial", "mackey_arena_cam66_precinct_aerial.png"),
    ]
    
    for cam_name, filename in cams:
        cam_obj = bpy.data.objects.get(cam_name)
        if not cam_obj:
            print(f"Warning: camera {cam_name} not found!")
            continue
        scene.camera = cam_obj
        filepath = os.path.join(artifact_dir, filename)
        scene.render.filepath = filepath
        print(f"Rendering {cam_name} -> {filepath}...")
        bpy.ops.render.render(write_still=True)
        print(f"Finished rendering {cam_name} (File exists: {os.path.exists(filepath)}, size: {os.path.getsize(filepath) if os.path.exists(filepath) else 0} bytes)")

if __name__ == "__main__":
    render_cams()
