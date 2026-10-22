"""
Render inspection and comparison views for Jerry S. Rawls Hall (RAWL)
"""

import bpy
import os

BLEND_FILE = os.path.abspath("modular/buildings/rawls_hall.blend")
OUT_DIR = os.path.abspath("modular/buildings/rawls_hall_evidence")
os.makedirs(OUT_DIR, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)
scene = bpy.context.scene

# Render settings
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100

# Set world background lighting
world = scene.world
if not world:
    world = bpy.data.worlds.new("RAWL_World")
    scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.75, 0.85, 0.95, 1.0)
    bg.inputs["Strength"].default_value = 1.0

cameras = [
    "Cam_RAWL_01_North_StateSt",
    "Cam_RAWL_02_NW_Curved_Rotunda",
    "Cam_RAWL_03_West_GrantSt_Skywalk",
    "Cam_RAWL_04_SE_Diagonal_Facade",
    "Cam_RAWL_05_Roof_Arched_Penthouse",
    "Cam_RAWL_06_Ortho_Footprint_Top",
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
