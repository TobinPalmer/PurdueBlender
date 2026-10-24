"""Render a plan-aligned third-floor library/circulation audit from saved asset."""

import bpy
from pathlib import Path
from mathutils import Vector

ROOT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
ASSET = ROOT / "modular/buildings/math_sciences.blend"
OUT = ROOT / "audit/batch3_math"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset = bpy.data.collections["Asset_math_sciences"]
scene = bpy.data.scenes.new("Math Third Floor Plan Review Round 8")
review = bpy.data.collections.new("R8 review selection")
scene.collection.children.link(review)

selected = []
for obj in asset.all_objects:
    name = obj.name
    if (
        name.startswith("MATH_2026_Library_")
        or name.startswith("MATH_2026_Inferred_Group_Room_")
        or name.startswith("MATH_2026_Testing_Room_352_")
        or name.startswith("MATH_2026_Third_Floor_")
    ):
        review.objects.link(obj)
        selected.append(obj)

# Keep the plan-derived transverse circulation strips visible in this audit.
floor_mesh = bpy.data.meshes.new("R8 third-floor review plane mesh")
floor_mesh.from_pydata(
    [(-10.5, -7.0, 6.585), (10.5, -7.0, 6.585),
     (10.5, 32.0, 6.585), (-10.5, 32.0, 6.585)],
    [], [(0, 1, 2, 3)],
)
floor = bpy.data.objects.new("R8 third-floor review plane", floor_mesh)
review.objects.link(floor)
floor.color = (0.83, 0.81, 0.75, 1)

# Recolor a temporary review scene only so partitions and circulation are clear.
for obj in selected:
    name = obj.name.lower()
    if "circulation_inlay" in name or "core_connector" in name:
        obj.color = (0.29, 0.35, 0.30, 1)
    elif "boundar" in name or "partition" in name or "frame" in name or "guard" in name:
        obj.color = (0.18, 0.22, 0.22, 1)
    elif "glaz" in name or "door" in name:
        obj.color = (0.30, 0.48, 0.53, 1)
    elif "book_spines" in name:
        obj.color = (0.58, 0.31, 0.18, 1)
    elif "bookcase" in name:
        obj.color = (0.38, 0.24, 0.13, 1)
    elif "seat" in name or "chair" in name:
        obj.color = (0.55, 0.38, 0.25, 1)
    elif "stair" in name or "elevator" in name:
        obj.color = (0.35, 0.38, 0.36, 1)
    elif "testing" in name:
        obj.color = (0.65, 0.58, 0.44, 1)
    elif "floor" in name or "carpet" in name:
        obj.color = (0.82, 0.79, 0.70, 1)
    else:
        obj.color = (0.64, 0.53, 0.38, 1)

for label, x, y in [
    ("311.3", -8.25, 14.5), ("311.4", -4.0, 15.55),
    ("311.5", 1.8, 15.55), ("311.7", 6.2, 15.55), ("311.8", 9.0, 14.5),
    ("NORTH STAIR", -4.0, 30.5), ("SOUTH CORE", 1.0, -5.9),
    ("ROOM 352", 6.1, -3.9),
]:
    data = bpy.data.curves.new("R8 plan label " + label, "FONT")
    data.body = label
    data.size = 0.40 if len(label) < 7 else 0.30
    text = bpy.data.objects.new("R8 plan label " + label, data)
    review.objects.link(text)
    text.location = (x, y, 6.72)
    text.color = (0.025, 0.035, 0.04, 1)

scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "OBJECT"
scene.display.shading.show_shadows = False
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = "WORLD"
scene.display.shading.curvature_ridge_factor = 1.25
scene.display.shading.curvature_valley_factor = 1.0
scene.display.shading.background_type = "WORLD"
scene.world = bpy.data.worlds.new("R8 neutral review world")
scene.world.color = (0.92, 0.93, 0.94)
scene.render.resolution_x = 1200
scene.render.resolution_y = 1600
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

def camera(name, location, target, ortho_scale):
    data = bpy.data.cameras.new(name)
    data.type = "ORTHO"
    data.ortho_scale = ortho_scale
    obj = bpy.data.objects.new(name, data)
    review.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    return obj

scene.camera = camera("R8 plan camera", (0.0, 12.5, 38.0), (0.0, 12.5, 6.5), 43.5)
scene.render.filepath = str(OUT / "library_plan_round8.png")
bpy.context.window.scene = scene
bpy.ops.render.render(write_still=True)

scene.camera = camera("R8 oblique camera", (33.0, -35.0, 26.0), (0.0, 12.0, 7.5), 48.0)
scene.render.filepath = str(OUT / "library_oblique_round8.png")
bpy.ops.render.render(write_still=True)
print("R8 library scene rendered", len(selected), "source objects")
