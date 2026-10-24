"""Render reopened R9 asset: readable brick elevation and third-floor library."""
import bpy
from pathlib import Path
from mathutils import Vector

ROOT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
ASSET = ROOT / "modular/buildings/math_sciences.blend"
OUT = ROOT / "audit/batch3_math"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset = bpy.data.collections["Asset_math_sciences"]

def make_camera(collection, name, location, target, scale):
    data = bpy.data.cameras.new(name)
    data.type = "ORTHO"
    data.ortho_scale = scale
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    return obj

def review_scene(name, objects):
    scene = bpy.data.scenes.new(name)
    collection = bpy.data.collections.new(name + " selection")
    scene.collection.children.link(collection)
    for obj in objects:
        collection.objects.link(obj)
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "WORLD"
    scene.display.shading.curvature_ridge_factor = 1.3
    scene.display.shading.curvature_valley_factor = 1.0
    scene.display.shading.background_type = "WORLD"
    scene.world = bpy.data.worlds.new(name + " neutral world")
    scene.world.color = (0.76, 0.79, 0.82)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    return scene, collection

# Close facade crop makes the brick and its scale easier to inspect than the
# full campus overview. No model objects are changed for this presentation.
exterior_scene, exterior_coll = review_scene("Math R9 brick appearance review", asset.all_objects)
exterior_scene.render.engine = "CYCLES"
exterior_scene.cycles.samples = 24
exterior_scene.world.use_nodes = True
exterior_scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value = (0.46,0.50,0.55,1)
exterior_scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.6
sun_data = bpy.data.lights.new("R9 facade sun", "SUN")
sun_data.energy = 1.8
sun_data.angle = 0.12
sun = bpy.data.objects.new("R9 facade sun", sun_data)
exterior_coll.objects.link(sun)
sun.rotation_euler = (0.35,-0.45,-0.5)
fill_data = bpy.data.lights.new("R9 facade fill", "AREA")
fill_data.energy = 6500
fill_data.shape = "DISK"
fill_data.size = 48
fill = bpy.data.objects.new("R9 facade fill", fill_data)
exterior_coll.objects.link(fill)
fill.location = (54,-38,45)
fill.rotation_euler = (Vector((0,-2,17))-fill.location).to_track_quat("-Z","Y").to_euler()
exterior_scene.camera = make_camera(exterior_coll, "R9 brick facade camera", (72, -38, 22), (0, -2, 17), 58)
exterior_scene.render.resolution_x = 1600
exterior_scene.render.resolution_y = 1200
exterior_scene.render.filepath = str(OUT / "exterior_brick_r9.png")

# Clear standalone review layout with a legible oblique view, distinct from the
# plan-view render. Review-only colors do not change saved asset materials.
names = ("MATH_2026_Library_", "MATH_2026_Inferred_Group_Room_",
         "MATH_2026_Testing_Room_352_", "MATH_2026_Third_Floor_")
selected = [o for o in asset.all_objects if o.name.startswith(names)]
interior, interior_coll = review_scene("Math R9 third-floor library review", selected)
interior.display.shading.light = "FLAT"
interior.display.shading.show_shadows = False
interior.display.shading.show_cavity = True

for obj in selected:
    lower = obj.name.lower()
    if "circulation_inlay" in lower or "core_connector" in lower:
        obj.color = (0.22, 0.43, 0.30, 1)
    elif "book_spines" in lower:
        obj.color = (0.57, 0.28, 0.13, 1)
    elif "bookcase" in lower:
        obj.color = (0.34, 0.19, 0.09, 1)
    elif "seat" in lower or "chair" in lower:
        obj.color = (0.54, 0.32, 0.17, 1)
    elif "glaz" in lower or "door" in lower:
        obj.color = (0.19, 0.42, 0.53, 1)
    elif "partition" in lower or "boundary" in lower or "frame" in lower or "guard" in lower:
        obj.color = (0.14, 0.18, 0.19, 1)
    elif "stair" in lower or "elevator" in lower:
        obj.color = (0.28, 0.31, 0.31, 1)
    elif "testing" in lower:
        obj.color = (0.72, 0.60, 0.39, 1)
    elif "floor" in lower or "carpet" in lower:
        obj.color = (0.79, 0.75, 0.64, 1)
    else:
        obj.color = (0.62, 0.48, 0.31, 1)

# Include a floor finish plane only in this review scene to distinguish walk
# area from the surrounding background. It is explicitly not part of the asset.
mesh = bpy.data.meshes.new("R9 review-only third-floor plane mesh")
mesh.from_pydata([(-10.5,-7,6.584),(10.5,-7,6.584),(10.5,32,6.584),(-10.5,32,6.584)], [], [(0,1,2,3)])
plane = bpy.data.objects.new("R9 review-only third-floor plane", mesh)
interior_coll.objects.link(plane)
plane.color = (0.86,0.82,0.72,1)

interior.camera = make_camera(interior_coll, "R9 library axon camera", (20,-12,19), (0,12,7), 32)
interior.render.resolution_x = 1600
interior.render.resolution_y = 1200
interior.render.filepath = str(OUT / "library_oblique_round9.png")

interior.display.shading.color_type = "OBJECT"
bpy.context.window.scene = exterior_scene
bpy.ops.render.render(write_still=True)
bpy.context.window.scene = interior
bpy.ops.render.render(write_still=True)
print("R9 review renders saved", len(selected), "library/circulation objects")
