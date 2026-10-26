"""Render temporary R9 SE curtain-wall views from the review candidate."""
import bpy
import json
from pathlib import Path
import math
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = Path(__file__).with_name("rawls_hall_r9_candidate.blend")
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
wall = bpy.data.objects["RAWL_Masonry_Exterior_Walls"]
glass = bpy.data.objects["RAWL_SE_Diagonal_CurtainWall_Glass"]
first = glass.data.polygons[0]
points0 = [glass.matrix_world @ glass.data.vertices[i].co for i in first.vertices]
axis = (points0[1] - points0[0]).normalized()
normal = (glass.matrix_world.to_3x3() @ first.normal).normalized()
mid = sum((glass.matrix_world @ glass.data.vertices[i].co for i in glass.data.polygons[0].vertices), Vector()) / 4

scene.render.engine = "CYCLES"
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x = 1440
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
for obj in bpy.data.objects:
    if obj.type == "LIGHT":
        obj.hide_render = True
world = bpy.data.worlds.new("RAWL_R9_Review_World") if "RAWL_R9_Review_World" not in bpy.data.worlds else bpy.data.worlds["RAWL_R9_Review_World"]
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.62, 0.72, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.45
sun_data = bpy.data.lights.new("RAWL_R9_Review_Sun", "SUN")
sun_data.energy = 2.0
sun = bpy.data.objects.new("RAWL_R9_Review_Sun", sun_data)
scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(28), math.radians(-34), math.radians(-35))
scene.view_settings.view_transform = "AgX"

def make_camera(name, location, target, ortho_scale=None, lens=55):
    data = bpy.data.cameras.new(name)
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    if ortho_scale is not None:
        data.type = "ORTHO"
        data.ortho_scale = ortho_scale
    else:
        data.type = "PERSP"
        data.lens = lens
    return obj

centers = [sum((glass.matrix_world @ glass.data.vertices[i].co for i in p.vertices), Vector()) / 4 for p in glass.data.polygons]
target = sum(centers, Vector()) / len(centers) + Vector((0, 0, 3.5))
cam = make_camera("R9_SE_Facade_Review", target - normal * 67 + Vector((0, 0, 5)), target, 62)
scene.camera = cam
scene.render.filepath = str(Path(__file__).with_name("se_curtainwall_full_round9.png"))
bpy.ops.render.render(write_still=True)

# Close detail looks toward the current first floor room; this records the
# visible through-pane result without adding or saving render-only objects.
pane = glass.data.polygons[0]  # first-floor pane into plan-documented room 1086
points = [glass.matrix_world @ glass.data.vertices[i].co for i in pane.vertices]
pane_center = sum(points, Vector()) / len(points)
camera_location = pane_center - normal * 7 + Vector((0, 0, 0.9))
interior_target = pane_center + normal * 3.5 + Vector((0, 0, 0.1))
cam2 = make_camera("R9_SE_Through_Glass_Review", camera_location, interior_target, None, 45)
fill_data = bpy.data.lights.new("RAWL_R9_Interior_Fill", "AREA")
fill_data.energy = 2600
fill_data.shape = "DISK"
fill_data.size = 7
fill = bpy.data.objects.new("RAWL_R9_Interior_Fill", fill_data)
scene.collection.objects.link(fill)
fill.location = interior_target + normal * 3 + Vector((0, 0, 3))
fill.rotation_euler = (interior_target - fill.location).to_track_quat("-Z", "Y").to_euler()
scene.camera = cam2
scene.render.resolution_x = 1000
scene.render.resolution_y = 800
scene.render.filepath = str(Path(__file__).with_name("se_curtainwall_through_glass_round9.png"))
bpy.ops.render.render(write_still=True)
print(json.dumps({"candidate": str(ASSET), "full_view": scene.render.filepath, "render_only_cameras": [cam.name, cam2.name]}, indent=2))
