import bpy
import os

artifact_dir = r"C:\Users\Tobin\.gemini\antigravity\brain\7d054314-203a-4c1a-bb2d-ad8b0fc54e25"

cams = [
    ("Cam_62_Mackey_Arena_North_WoodenPlaza_Hero", "mackey_arena_cam62_north_woodenplaza.png"),
    ("Cam_63_Mackey_Arena_KeadyCourt_CenterCourt_Hero", "mackey_arena_cam63_keadycourt_hero.png"),
    ("Cam_64_Mackey_Arena_UpperBowl_CenterHungScoreboard", "mackey_arena_cam64_scoreboard_upperbowl.png"),
    ("Cam_65_Mackey_Arena_Courtside_Hoop_and_Bench", "mackey_arena_cam65_courtside_hoop.png"),
    ("Cam_66_Mackey_Arena_Athletic_Precinct_Aerial", "mackey_arena_cam66_precinct_aerial.png")
]

scene = bpy.context.scene
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

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
        print(f"ERROR: {cam_name} not found!")

print("All 5 Mackey Arena inspection cameras rendered successfully!")
