import os
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
ASSET = ROOT / "modular/buildings/neil_armstrong_hall.blend"
OUT = ROOT / "audit/neil_armstrong_hall_refine/renders_r1"
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 32
scene.render.resolution_x = 1800
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.render.image_settings.file_format = "PNG"
world = scene.world or bpy.data.worlds.new("R11_Review_World")
scene.world = world
world.use_nodes = True
next(n for n in world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (0.28, 0.35, 0.46, 1)
next(n for n in world.node_tree.nodes if n.type == "BACKGROUND").inputs["Strength"].default_value = 0.35

# Temporary presentation geometry is kept outside the source collection and is
# never saved into the building library.
ground_mat = bpy.data.materials.new("R11 temporary neutral review ground")
ground_mat.diffuse_color = (0.19, 0.22, 0.25, 1)
bpy.ops.mesh.primitive_plane_add(size=600, location=(0, 0, -0.18))
ground = bpy.context.object
ground.name = "R11_TEMP_REVIEW_GROUND"
ground.data.materials.append(ground_mat)

def area(name, location, target, energy, size):
    bpy.ops.object.light_add(type="AREA", location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.energy = energy
    obj.data.shape = "DISK"
    obj.data.size = size
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    return obj

area("R11_TEMP_KEY", (-30, 35, 75), (0, 0, 7), 100000, 50)
area("R11_TEMP_FILL", (55, 15, 38), (0, 0, 8), 42000, 65)

def render(name, location, target, lens):
    camera_data = bpy.data.cameras.new(f"{name}_DATA")
    camera = bpy.data.objects.new(f"{name}_TEMP_CAMERA", camera_data)
    scene.collection.objects.link(camera)
    camera.location = location
    camera_data.lens = lens
    camera_data.clip_end = 1000
    camera.rotation_euler = (Vector(target) - Vector(location)).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    scene.render.filepath = str(OUT / f"{name}.png")
    bpy.ops.render.render(write_still=True)

render("northwest_entrance_r1", (-29, 49, 12), (-1.5, 4, 8), 48)
render("north_entry_context_r1", (-48, 76, 27), (0, -1, 8), 46)
