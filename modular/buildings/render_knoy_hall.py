"""
Render inspection and comparison views for Maurice G. Knoy Hall of Technology (KNOY)
"""

import bpy
import os
import math

BLEND_FILE = os.path.abspath("modular/buildings/knoy_hall.blend")
OUT_DIR = os.path.abspath("modular/buildings/knoy_hall_evidence")
os.makedirs(OUT_DIR, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)
scene = bpy.context.scene

# Render settings
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100

# Set up world lighting
world = scene.world
if not world:
    world = bpy.data.worlds.new("KNOY_World")
    scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.75, 0.85, 0.95, 1.0) # Nice sky blue tint
    bg.inputs["Strength"].default_value = 1.0

# Add directional sunlight for architectural shadows
sun_data = bpy.data.lights.new(name="KNOY_Sun", type='SUN')
sun_data.energy = 3.5
sun_data.color = (1.0, 0.96, 0.90)
sun_obj = bpy.data.objects.new(name="KNOY_Sun", object_data=sun_data)
sun_obj.rotation_euler = (math.radians(50.0), math.radians(20.0), math.radians(40.0))
scene.collection.objects.link(sun_obj)

cameras = [
    "Cam_KNOY_01_Ortho_Footprint_Top",
    "Cam_KNOY_02_Grant_Street_East",
    "Cam_KNOY_03_North_Diagonal_Facade",
    "Cam_KNOY_04_South_Plaza_Elevation",
    "Cam_KNOY_05_West_Courtyard_Skywalk",
    "Cam_KNOY_06_Roof_Penthouse_Solar",
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

print("=== ALL KNOY RENDERS COMPLETED ===")
