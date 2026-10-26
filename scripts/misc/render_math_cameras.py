"""
Render all 5 inspection cameras for Mathematical Sciences Building (MATH)
Cam_92: Hero South-West University Street Arrival View
Cam_93: Ground Floor MATH 175 Major Tiered Lecture Hall Interior
Cam_94: 3rd-Floor Mathematical Sciences Library Interior
Cam_95: 10th-Floor Faculty Colloquium Sky Lounge Interior
Cam_96: Precinct Aerial Context Overview
"""

import bpy
import os

BLEND_PATH = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
OUTPUT_DIR = r"C:\Users\Tobin\.gemini\antigravity\brain\7d054314-203a-4c1a-bb2d-ad8b0fc54e25"

cams = [
    ("Cam_92_MATH_UniversitySt_Hero", "math_cam92_universityst_hero.png"),
    ("Cam_93_MATH_175_LectureHall_Interior", "math_cam93_lecturehall_175.png"),
    ("Cam_94_MATH_Library_Study_Interior", "math_cam94_library_study.png"),
    ("Cam_95_MATH_10thFloor_SkyLounge_Interior", "math_cam95_10thfloor_skylounge.png"),
    ("Cam_96_MATH_Precinct_Aerial", "math_cam96_precinct_aerial.png"),
]

def render_all():
    bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)
    scene = bpy.context.scene

    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, "RenderEngineEEVEENext") else 'BLENDER_EEVEE'
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100

    # Ensure lighting and world ambient
    if scene.world and scene.world.node_tree:
        bg = scene.world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs["Color"].default_value = (0.75, 0.85, 1.0, 1.0)
            bg.inputs["Strength"].default_value = 1.0

    for cam_name, out_file in cams:
        cam_obj = bpy.data.objects.get(cam_name)
        if not cam_obj:
            print(f"Error: Camera {cam_name} not found!")
            continue
        scene.camera = cam_obj
        out_path = os.path.join(OUTPUT_DIR, out_file)
        scene.render.filepath = out_path
        print(f"Rendering {cam_name} -> {out_path}...")
        bpy.ops.render.render(write_still=True)
        print(f"Done rendering {cam_name}!")

if __name__ == "__main__":
    render_all()
