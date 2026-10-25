import bpy
from pathlib import Path
from mathutils import Vector

ROOT = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
ASSET = ROOT / "modular/buildings/neil_armstrong_hall.blend"
OUT = ROOT / "audit/neil_armstrong_hall_refine/renders_r2"
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 6
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 900, 580, 100
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
world = scene.world or bpy.data.worlds.new("R11_Diag_World")
scene.world = world
world.use_nodes = True
world.node_tree.nodes.get("Background").inputs["Color"].default_value = (0.23, 0.30, 0.39, 1)
world.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.4

for name, loc, aim, watts, size in [
    ("R11_Diag_Key", (-25, 24, 70), (0, 0, 8), 85000, 55),
    ("R11_Diag_Fill", (60, -10, 38), (0, 0, 8), 35000, 70),
]:
    bpy.ops.object.light_add(type="AREA", location=loc)
    light = bpy.context.object
    light.name = name
    light.data.energy, light.data.shape, light.data.size = watts, "DISK", size
    light.rotation_euler = (Vector(aim) - light.location).to_track_quat("-Z", "Y").to_euler()

mat = bpy.data.materials.new("R11_Diag_Ground")
mat.diffuse_color = (0.20, 0.24, 0.26, 1)
bpy.ops.mesh.primitive_plane_add(size=300, location=(0, 0, -0.2))
bpy.context.object.name = "R11_Diag_TEMP_GROUND"
bpy.context.object.data.materials.append(mat)

def render(name, loc, aim, hide_lidar=False):
    for obj in bpy.data.objects:
        if obj.name.startswith("ARMS_R5_Coarse_LiDAR_"):
            obj.hide_render = hide_lidar
    data = bpy.data.cameras.new(name + "_Data")
    cam = bpy.data.objects.new(name + "_TempCamera", data)
    scene.collection.objects.link(cam)
    cam.location = loc
    data.lens, data.clip_end = 48, 1000
    cam.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam
    scene.render.filepath = str(OUT / f"{name}.png")
    bpy.ops.render.render(write_still=True)

render("north_without_lidar", (0, 55, 26), (0, -3, 8), True)
render("south_without_lidar", (0, -100, 32), (0, -1, 8), True)
render("west_without_lidar", (-125, 0, 30), (0, -5, 8), True)
render("east_without_lidar", (125, 0, 30), (0, -5, 8), True)
