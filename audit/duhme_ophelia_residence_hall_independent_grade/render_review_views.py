"""Render fresh visual inspection views from the saved candidate without saving it."""
import bpy
import math
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).parent
collection = bpy.data.collections.get("Asset_massing_duhme_ophelia_residence_hall_1bb4e9c")
if collection is None:
    raise RuntimeError("Expected Duhme export collection was not found")
scene = bpy.context.scene
available_engines = [item.identifier for item in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
scene.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in available_engines else available_engines[0]
scene.render.resolution_x = 1200
scene.render.resolution_y = 850
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.view_settings.view_transform = "AgX"
scene.render.filepath = str(ROOT / "review_view.png")

# Render only the exported building collection. This avoids judging campus surroundings
# or builder-created presentation objects as part of the building asset.
for obj in scene.objects:
    obj.hide_render = obj.name not in {o.name for o in collection.all_objects}

center = Vector((-595.04, -202.44, 7.4))
world = scene.world or bpy.data.worlds.new("Duhme independent review world")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs[0].default_value = (0.24, 0.29, 0.36, 1.0)
bg.inputs[1].default_value = 0.45

def aim(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat("-Z", "Y").to_euler()

def make_area(name, location, power, size):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = power
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    aim(obj, center)
    return obj

make_area("Review key", (-650, -275, 75), 9500, 55)
make_area("Review fill", (-530, -155, 55), 5500, 60)
make_area("Review rim", (-590, -100, 65), 7500, 40)

cam_data = bpy.data.cameras.new("Independent review camera")
cam = bpy.data.objects.new("Independent review camera", cam_data)
scene.collection.objects.link(cam)
cam_data.type = "ORTHO"
cam_data.ortho_scale = 105
scene.camera = cam

for filename, direction, scale in [
    ("review_three_quarter.png", (-0.9, -1.0, 0.48), 110),
    ("review_north_elevation.png", (0.0, -1.0, 0.12), 95),
    ("review_east_elevation.png", (-1.0, 0.0, 0.12), 95),
    ("review_top.png", (0.0, 0.0, 1.0), 98),
]:
    cam.location = center + Vector(direction).normalized() * 150
    aim(cam, center)
    cam_data.ortho_scale = scale
    scene.render.filepath = str(ROOT / filename)
    bpy.ops.render.render(write_still=True)
    print("RENDERED", filename)
