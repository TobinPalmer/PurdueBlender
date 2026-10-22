"""
Purdue University Digital Twin - Felix Haas Hall (HAAS - 1909)
Attempt 3: Gold Standard Final Polish & Camera Calibration
"""

import bpy
import math
import os

BLEND_PATH = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
OUTPUT_DIR = r"C:\Users\Tobin\.gemini\antigravity\brain\7d054314-203a-4c1a-bb2d-ad8b0fc54e25"

def run_attempt3():
    bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)
    col_cams = bpy.data.collections.get("00_Inspection_Cameras")

    # 1. Fix 1903 Memorial Plaque text orientation (un-mirror so it faces East)
    p_header = bpy.data.objects.get("HAAS_1903_Plaque_Header")
    if p_header:
        p_header.location = (5.25, -1.5, 2.9)
        p_header.rotation_euler = (math.pi/2, 0, math.pi/2)

    p_body = bpy.data.objects.get("HAAS_1903_Plaque_Body")
    if p_body:
        p_body.location = (5.25, -1.4, 2.5)
        p_body.rotation_euler = (math.pi/2, 0, math.pi/2)

    # 2. Setup Cameras
    def set_cam(name, loc, rot_deg, lens=22.0):
        c = bpy.data.objects.get(name)
        if not c:
            cd = bpy.data.cameras.new(name=name)
            c = bpy.data.objects.new(name=name, object_data=cd)
            col_cams.objects.link(c)
        c.data.lens = lens
        c.data.clip_start = 0.1
        c.data.clip_end = 1500.0
        c.location = loc
        c.rotation_euler = (math.radians(rot_deg[0]), math.radians(rot_deg[1]), math.radians(rot_deg[2]))
        return c

    # Cam 97: Hero East Arrival View
    set_cam("Cam_97_HAAS_East_MemorialSteps_Hero", (-180.0, -74.0, 4.0), (86.0, 0.0, 68.0), lens=21.0)

    # Cam 98: 1903 Memorial Rotunda Interior
    set_cam("Cam_98_HAAS_1903_Memorial_Rotunda_Interior", (-205.5, -64.02, 2.3), (90.0, 0.0, 90.0), lens=18.0)

    # Cam 99: Computer Science Collaborative Commons Interior
    set_cam("Cam_99_HAAS_CS_Commons_Interior", (-234.0, -82.0, 6.8), (82.0, 0.0, -45.0), lens=18.0)

    # Cam 100: Felix Haas Faculty & Graduate Seminar Suite Interior
    # Eye height at Z = 11.25m overlooking table top, chairs, banker's lamps, and portrait
    set_cam("Cam_100_HAAS_Faculty_Seminar_Interior", (-235.0, -68.0, 11.25), (83.0, 0.0, -38.0), lens=20.0)

    # Cam 101: Precinct Aerial Context
    set_cam("Cam_101_HAAS_Precinct_Aerial", (-155.0, -120.0, 58.0), (56.0, 0.0, 34.0), lens=22.0)

    bpy.ops.wm.save_mainfile(filepath=BLEND_PATH)
    print("Master Blend saved in PurdueMap.")

    # 3. Render All 5 Inspection Cameras
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, "RenderEngineEEVEENext") else 'BLENDER_EEVEE'
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100

    if scene.world and scene.world.node_tree:
        bg = scene.world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs["Color"].default_value = (0.75, 0.85, 1.0, 1.0)
            bg.inputs["Strength"].default_value = 1.0

    cams_to_render = [
        ("Cam_97_HAAS_East_MemorialSteps_Hero", "haas_cam97_east_memorialsteps_hero.png"),
        ("Cam_98_HAAS_1903_Memorial_Rotunda_Interior", "haas_cam98_rotunda_1903_memorial.png"),
        ("Cam_99_HAAS_CS_Commons_Interior", "haas_cam99_cs_commons_interior.png"),
        ("Cam_100_HAAS_Faculty_Seminar_Interior", "haas_cam100_faculty_seminar_interior.png"),
        ("Cam_101_HAAS_Precinct_Aerial", "haas_cam101_precinct_aerial.png"),
    ]

    for cam_name, out_file in cams_to_render:
        c_obj = bpy.data.objects.get(cam_name)
        if not c_obj:
            continue
        scene.camera = c_obj
        out_path = os.path.join(OUTPUT_DIR, out_file)
        scene.render.filepath = out_path
        print(f"Rendering {cam_name} -> {out_path}...")
        bpy.ops.render.render(write_still=True)
        print(f"Rendered {cam_name} successfully!")

if __name__ == "__main__":
    run_attempt3()
