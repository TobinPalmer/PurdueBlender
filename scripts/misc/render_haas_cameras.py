"""
Render all 5 inspection cameras for Felix Haas Hall (HAAS - 1909 / Memorial Gymnasium)
Cam_97: Hero East Arrival Perspective (Memorial 17 Steps, Carved Portal, Roof, Cupola)
Cam_98: 1903 Memorial Rotunda Interior (Memorial Bronze Plaque, Vitrines, Chandelier)
Cam_99: Computer Science Collaborative Commons Interior (Floor 2, Maple Floor, Trusses, Pods)
Cam_100: Felix Haas Faculty & Graduate Seminar Suite Interior (Floor 3, Walnut Suite, Portrait)
Cam_101: Precinct Aerial Context Overview (Armory - Haas - Math University St Corridor)
"""

import bpy
import os

BLEND_PATH = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
OUTPUT_DIR = r"C:\Users\Tobin\.gemini\antigravity\brain\7d054314-203a-4c1a-bb2d-ad8b0fc54e25"

cams = [
    ("Cam_97_HAAS_East_MemorialSteps_Hero", "haas_cam97_east_memorialsteps_hero.png"),
    ("Cam_98_HAAS_1903_Memorial_Rotunda_Interior", "haas_cam98_rotunda_1903_memorial.png"),
    ("Cam_99_HAAS_CS_Commons_Interior", "haas_cam99_cs_commons_interior.png"),
    ("Cam_100_HAAS_Faculty_Seminar_Interior", "haas_cam100_faculty_seminar_interior.png"),
    ("Cam_101_HAAS_Precinct_Aerial", "haas_cam101_precinct_aerial.png"),
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
