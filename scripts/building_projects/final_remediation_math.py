"""
Purdue University Digital Twin - Mathematical Sciences Building (MATH) Final Gold Standard Remediation
1. Fix MATH 175 blackboard equation rotation (un-mirror text by setting rot_z = pi)
2. Fine-tune Cam 93 position & pitch to frame stage, smart podium, and blackboard derivations prominently
3. Fine-tune Cam 92 hero view pitch (83 deg) to capture full 10-story tower and rooftop penthouse
4. Fine-tune Cam 94 library view to showcase open book shelves with multi-colored books and study tables
5. Re-render all 5 cameras to finalize gold standard artifacts
"""

import bpy
import math
import os

BLEND_PATH = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
OUTPUT_DIR = r"C:\Users\Tobin\.gemini\antigravity\brain\7d054314-203a-4c1a-bb2d-ad8b0fc54e25"

def run_final():
    bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)
    print("Opened blend for final remediation...")

    root_obj = bpy.data.objects.get("MATH_Root")
    col_int = bpy.data.collections.get("61_Math_Sciences_Interiors")
    mat_chalk = bpy.data.materials.get("MATH_Chalk_Emissive")

    # 1. Fix MATH 175 blackboard equation rotation so text faces North (+Y towards camera)
    for b_idx in range(4):
        eq_obj = bpy.data.objects.get(f"MATH_175_Equation_{b_idx+1}")
        if eq_obj:
            # When looking South (-Y), text facing camera (+Y) must have rotation (pi/2, 0, pi)
            bx = -9.0 + 1.2 + b_idx * 2.5
            eq_obj.location = (bx + 0.95, -25.88, 2.3)
            eq_obj.rotation_euler = (math.pi/2, 0, math.pi)
            print(f"Corrected orientation of {eq_obj.name}")

    # 2. Camera Recalibrations
    cams = {
        # Cam 92: Hero South-West University Street Arrival
        # Captures full 10 stories + penthouse from street level
        "Cam_92_MATH_UniversitySt_Hero": ((-238.0, -145.0, 11.5), (math.radians(83), 0, math.radians(-70)), 20.0),
        
        # Cam 93: MATH 175 Major Tiered Lecture Hall
        # Centered down the aisle framing 8 tiers, smart podium, stage, and chalkboard derivations
        "Cam_93_MATH_175_LectureHall_Interior": ((-185.62, -137.0, 2.85), (math.radians(97), 0, math.radians(180)), 19.0),
        
        # Cam 94: Mathematical Sciences Library (Floor 3)
        # 3/4 perspective capturing both study tables with banker's lamps and colorful book stacks
        "Cam_94_MATH_Library_Study_Interior": ((-178.0, -121.0, 12.3), (math.radians(80), 0, math.radians(20)), 19.0),
        
        # Cam 95: 10th-Floor Faculty Colloquium Sky Lounge
        # Conference table, brass chandelier, burgundy chairs, and ribbon windows
        "Cam_95_MATH_10thFloor_SkyLounge_Interior": ((-185.12, -133.79, 31.2), (math.radians(75), 0, math.radians(-38)), 19.0),
        
        # Cam 96: Precinct Aerial Context
        # Complete tower massing, precast waffle grid, and campus connectivity
        "Cam_96_MATH_Precinct_Aerial": ((-115.0, -210.0, 68.0), (math.radians(56), 0, math.radians(35)), 24.0)
    }

    for name, (loc, rot, lens) in cams.items():
        cam = bpy.data.objects.get(name)
        if cam:
            cam.location = loc
            cam.rotation_euler = rot
            cam.data.lens = lens
            print(f"Recalibrated {name}: loc={loc}, rot={rot}, lens={lens}")

    # Save Master Blend File
    bpy.ops.wm.save_mainfile(filepath=BLEND_PATH)
    print("Master Blend File updated and saved successfully!")

    # 3. Render all 5 Cameras
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, "RenderEngineEEVEENext") else 'BLENDER_EEVEE'
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100

    render_list = [
        ("Cam_92_MATH_UniversitySt_Hero", "math_cam92_universityst_hero.png"),
        ("Cam_93_MATH_175_LectureHall_Interior", "math_cam93_lecturehall_175.png"),
        ("Cam_94_MATH_Library_Study_Interior", "math_cam94_library_study.png"),
        ("Cam_95_MATH_10thFloor_SkyLounge_Interior", "math_cam95_10thfloor_skylounge.png"),
        ("Cam_96_MATH_Precinct_Aerial", "math_cam96_precinct_aerial.png"),
    ]

    for cam_name, out_file in render_list:
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
    run_final()
