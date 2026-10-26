"""
Purdue University Digital Twin - Felix Haas Hall (HAAS - 1909)
Gold Standard Polish & Camera Realignment
"""

import bpy
import math
import os

BLEND_PATH = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
OUTPUT_DIR = r"C:\Users\Tobin\.gemini\antigravity\brain\7d054314-203a-4c1a-bb2d-ad8b0fc54e25"

def run_polish():
    bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)
    col_ext = bpy.data.collections.get("63_Felix_Haas_Hall_Exterior")
    col_int = bpy.data.collections.get("64_Felix_Haas_Hall_Interiors")
    col_cams = bpy.data.collections.get("00_Inspection_Cameras")

    root_obj = bpy.data.objects.get("HAAS_Root")
    mat_gold = bpy.data.materials.get("HAAS_Purdue_Gold") or bpy.data.materials.get("Purdue_Old_Gold")
    mat_steel = bpy.data.materials.get("HAAS_Structural_Steel")

    # 1. Ensure trusses stop at the Seminar room partition wall (X = -4.8m)
    # Trusses span X from -4.8 to +18.0 (length = 22.8m, center X = 6.6m)
    for ti, ty in enumerate([-16.0, -5.3, 5.3, 16.0]):
        top = bpy.data.objects.get(f"HAAS_Truss_TopChord_{ti+1}")
        bot = bpy.data.objects.get(f"HAAS_Truss_BottomChord_{ti+1}")
        if top:
            top.location = (6.6, ty, 10.8)
            top.scale = (22.8, 0.35, 0.4)
        if bot:
            bot.location = (6.6, ty, 9.2)
            bot.scale = (22.8, 0.35, 0.4)

    # 2. Re-position East Portal Inscription "MEMORIAL GYMNASIUM" for maximum hero readability
    txt = bpy.data.objects.get("HAAS_Portal_Inscription")
    if txt:
        txt.location = (22.5, 3.8, 8.8)
        txt.data.size = 0.48
        txt.data.extrude = 0.06

    # 3. Setup Cameras
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

    # Cam 98: 1903 Memorial Rotunda Interior - Dead Center Symmetrical View
    # Sited on centerline Y = -64.02 at X = -206.0, looking straight West at plaque and chandelier
    set_cam("Cam_98_HAAS_1903_Memorial_Rotunda_Interior", (-205.5, -64.02, 2.3), (90.0, 0.0, 90.0), lens=18.0)

    # Cam 99: Computer Science Collaborative Commons Interior
    set_cam("Cam_99_HAAS_CS_Commons_Interior", (-234.0, -82.0, 6.8), (82.0, 0.0, -45.0), lens=18.0)

    # Cam 100: Felix Haas Faculty & Graduate Seminar Suite Interior
    # Inside seminar room, unobstructed view of walnut table, banker's lamps, chairs, and portrait
    set_cam("Cam_100_HAAS_Faculty_Seminar_Interior", (-235.0, -68.0, 10.4), (88.0, 0.0, -38.0), lens=20.0)

    # Cam 101: Precinct Aerial Context
    set_cam("Cam_101_HAAS_Precinct_Aerial", (-155.0, -120.0, 58.0), (56.0, 0.0, 34.0), lens=22.0)

    bpy.ops.wm.save_mainfile(filepath=BLEND_PATH)
    print("Master Blend saved in Documents\\Blender.")

    # 4. Render All 5 Inspection Cameras
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
        print(f"Rendered {cam_name}!")

if __name__ == "__main__":
    run_polish()
