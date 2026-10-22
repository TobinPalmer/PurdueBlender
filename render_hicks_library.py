"""
Render inspection and comparison views for John W. Hicks Undergraduate Library (HIKS)
"""

import bpy
import os
import math

BLEND_FILE = os.path.abspath("modular/buildings/hicks_library.blend")
OUT_DIR = os.path.abspath("modular/buildings/hicks_library_evidence")
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
    world = bpy.data.worlds.new("HIKS_World")
    scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.78, 0.86, 0.94, 1.0) # Sky blue
    bg.inputs["Strength"].default_value = 1.0

# Add a sun light if none exists
sun_obj = bpy.data.objects.get("HIKS_Sun_Light")
if not sun_obj:
    sun_data = bpy.data.lights.new("HIKS_Sun_Light", 'SUN')
    sun_data.energy = 3.5
    sun_data.color = (1.0, 0.98, 0.92)
    sun_obj = bpy.data.objects.new("HIKS_Sun_Light", sun_data)
    sun_obj.location = (88.0, -318.0, 50.0)
    sun_obj.rotation_euler = (math.radians(50.0), math.radians(15.0), math.radians(-35.0))
    scene.collection.objects.link(sun_obj)

# Create an explicit GIS Footprint Reference Wireframe Curve/Mesh for top-down comparison
gis_wire_name = "HIKS_GIS_Footprint_Reference_Wire"
gis_wire = bpy.data.objects.get(gis_wire_name)
if not gis_wire:
    import json
    gis_path = "modular/buildings/target_buildings_gis.json"
    with open(gis_path, "r") as f:
        gis_poly = json.load(f)["HIKS"]["world_polygon"]
    
    mesh = bpy.data.meshes.new(gis_wire_name)
    verts = [(p[0], p[1], 3.20) for p in gis_poly[:-1]]
    edges = [(i, (i + 1) % len(verts)) for i in range(len(verts))]
    mesh.from_pydata(verts, edges, [])
    mesh.update()
    
    gis_wire = bpy.data.objects.new(gis_wire_name, mesh)
    
    # Yellow glowing wireframe material
    mat_wire = bpy.data.materials.new("Mat_GIS_Footprint_Overlay")
    mat_wire.use_nodes = True
    nodes = mat_wire.node_tree.nodes
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    emit = nodes.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value = (1.0, 0.85, 0.0, 1.0) # Bright gold/yellow
    emit.inputs['Strength'].default_value = 5.0
    mat_wire.node_tree.links.new(emit.outputs['Emission'], out.inputs['Surface'])
    gis_wire.data.materials.append(mat_wire)
    
    # Give wire thickness
    mod = gis_wire.modifiers.new("Wire_Thickness", 'WIREFRAME')
    mod.thickness = 0.15
    mod.use_boundary = True
    scene.collection.objects.link(gis_wire)

cameras = [
    ("Cam_HIKS_01_Footprint_TopDown", True), # show wire overlay
    ("Cam_HIKS_02_North_Plaza_Hero", False),
    ("Cam_HIKS_03_South_MitchDaniels_Hero", False),
    ("Cam_HIKS_04_Northwest_Perspective", False),
    ("Cam_HIKS_05_Subterranean_Axonometric", False),
    ("Cam_HIKS_06_Subterranean_Interior", False),
    ("Cam_HIKS_07_North_Entrance_Close", False)
]

for cam_name, show_wire in cameras:
    cam_obj = bpy.data.objects.get(cam_name)
    if not cam_obj:
        print(f"Warning: camera {cam_name} not found")
        continue
    gis_wire.hide_render = not show_wire
    scene.camera = cam_obj
    out_path = os.path.join(OUT_DIR, f"{cam_name}.png")
    scene.render.filepath = out_path
    print(f"Rendering {cam_name} (wire={show_wire}) to {out_path}...")
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {out_path}")

print("=== ALL RENDERS COMPLETED ===")
