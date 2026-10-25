import bpy
from pathlib import Path
from mathutils import Vector

ROOT = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
ASSET = ROOT / "modular/buildings/neil_armstrong_hall.blend"
OUT = ROOT / "audit/neil_armstrong_hall_refine/renders_r3"
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 24
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1300, 800, 100
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.render.image_settings.file_format = "PNG"
world = scene.world or bpy.data.worlds.new("R11_FinalReview_World")
scene.world = world
world.use_nodes = True
background = next(node for node in world.node_tree.nodes if node.type == "BACKGROUND")
background.inputs["Color"].default_value = (0.29, 0.35, 0.43, 1)
background.inputs["Strength"].default_value = 0.28

for name, loc, target, energy, size in [
    ("R11_Final_Key", (-25, 35, 55), (0, 0, 8), 18000, 48),
    ("R11_Final_Fill", (50, 5, 30), (0, 0, 8), 7000, 60),
]:
    bpy.ops.object.light_add(type="AREA", location=loc)
    light = bpy.context.object
    light.name = name
    light.data.energy = energy
    light.data.shape = "DISK"
    light.data.size = size
    light.rotation_euler = (Vector(target) - light.location).to_track_quat("-Z", "Y").to_euler()

ground_mat = bpy.data.materials.new("R11_Final_Review_Ground")
ground_mat.diffuse_color = (0.15, 0.18, 0.20, 1)
bpy.ops.mesh.primitive_plane_add(size=300, location=(0, 0, -0.2))
ground = bpy.context.object
ground.name = "R11_TEMP_REVIEW_GROUND"
ground.data.materials.append(ground_mat)

def render(name, location, aim, lens):
    camera_data = bpy.data.cameras.new(name + "_Data")
    camera = bpy.data.objects.new(name + "_TEMP_CAMERA", camera_data)
    scene.collection.objects.link(camera)
    camera.location = location
    camera_data.lens = lens
    camera_data.clip_end = 1000
    camera.rotation_euler = (Vector(aim) - Vector(location)).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    scene.render.filepath = str(OUT / f"{name}.png")
    bpy.ops.render.render(write_still=True)

render("north_entry_refined_r3", (-28, 42, 18), (0, 1, 9), 48)
