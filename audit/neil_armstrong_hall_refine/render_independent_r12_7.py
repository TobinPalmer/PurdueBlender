import bpy
from mathutils import Vector
from pathlib import Path

ROOT = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
ASSET = ROOT / "modular/buildings/neil_armstrong_hall.blend"
OUT = ROOT / "audit/neil_armstrong_hall_refine/renders_independent_r12_7"
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1300, 850, 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.world = scene.world or bpy.data.worlds.new("R12_Review_World")
scene.world.use_nodes = True
bg = next(n for n in scene.world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs["Color"].default_value = (0.25, 0.31, 0.39, 1)
bg.inputs["Strength"].default_value = 0.48

for name, loc, energy, size in [
    ("R12_Key", (-40, 60, 90), 22000, 80),
    ("R12_Fill", (70, -30, 65), 10000, 70),
    ("R12_Rim", (0, -70, 50), 9000, 50),
    ("R12_Underside_Fill", (-18, 2, 9), 7000, 45),
]:
    bpy.ops.object.light_add(type="AREA", location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.data.energy = energy
    ob.data.shape = "DISK"
    ob.data.size = size
    ob.rotation_euler = (Vector((0, 0, 9)) - ob.location).to_track_quat("-Z", "Y").to_euler()

ground_mat = bpy.data.materials.new("R12_Temp_Ground")
ground_mat.diffuse_color = (0.17, 0.19, 0.20, 1)
bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, -0.25))
ground = bpy.context.object
ground.name = "R12_TEMP_REVIEW_GROUND"
ground.data.materials.append(ground_mat)

def render(name, location, target, lens=50, ortho=None):
    data = bpy.data.cameras.new(name + "_Data")
    cam = bpy.data.objects.new(name + "_TEMP_CAMERA", data)
    scene.collection.objects.link(cam)
    cam.location = location
    data.lens = lens
    data.clip_end = 2000
    if ortho:
        data.type = "ORTHO"
        data.ortho_scale = ortho
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam
    scene.render.filepath = str(OUT / f"{name}.png")
    bpy.ops.render.render(write_still=True)

render("r12_geotag_view01", (-95.4, 43.8, 1.7), (-2, -8, 10), lens=38)
render("r12_courtyard_clear_view", (-100, -35, 1.7), (0, -5, 10), lens=24)
render("r12_geotag_view03", (-152.1, 48.8, 1.7), (0, -8, 10), lens=48)
render("r12_northwest_source03", (-150, 50, 24), (0, -2, 10), lens=48)
render("r12_north_elevation", (0, 115, 30), (0, 0, 9), lens=50)
render("r12_south_elevation", (0, -120, 30), (0, -4, 9), lens=50)
render("r12_east_elevation", (125, -4, 28), (0, -4, 9), lens=50)
render("r12_west_elevation", (-130, -4, 28), (0, -4, 9), lens=50)
render("r12_top_registered", (0, -5, 155), (0, -5, 0), lens=50, ortho=185)
print("Rendered R12 multi-side baseline to", OUT)


