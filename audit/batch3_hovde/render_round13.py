import bpy
from mathutils import Vector
from pathlib import Path

PROJECT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
bpy.ops.wm.open_mainfile(filepath=str(PROJECT / "modular/buildings/hovde_hall.blend"))
scene = bpy.context.scene
root = bpy.data.objects["HOVD_Root"]
port = bpy.data.objects["HOVD_Portico_Pediment_Base"].matrix_world.translation.copy()
side = (root.matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized()
along = (root.matrix_world.to_3x3() @ Vector((0, 1, 0))).normalized()

scene.render.engine = "BLENDER_EEVEE"
scene.eevee.taa_render_samples = 128
scene.render.resolution_x, scene.render.resolution_y = 1800, 1200
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.view_settings.exposure = 0.85
scene.render.image_settings.color_mode = "RGBA"

world = bpy.data.worlds.new("Hovde Round 13 Reference Daylight") if not bpy.data.worlds else bpy.data.worlds[0]
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.34, 0.43, 0.58, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.65

def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()

def area(name, loc, target, power, size, color):
    data = bpy.data.lights.new(name, "AREA")
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = loc
    data.energy = power
    data.shape = "DISK"
    data.size = size
    data.color = color
    aim(obj, target)
    return obj

def camera(name, loc, target, lens):
    data = bpy.data.cameras.new(name)
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = loc
    data.type = "PERSP"
    data.lens = lens
    data.sensor_width = 36
    aim(obj, target)
    return obj

target = port + Vector((0, 0, -5.0))
# Near-frontal 34 mm view modeled after Herzog's geotagged 2016 approach photo.
eye = target + side * 75 + Vector((0, 0, -8.4))
cam = camera("HOVD_R13_SameAngle_34mm", eye, target, 34)
scene.camera = cam
area("HOVD_R13_Soft_Sun", target + side*35 + along*12 + Vector((0,0,38)), target, 5200, 32, (1.0,0.87,0.70))
area("HOVD_R13_Sky_Fill", target - side*24 - along*15 + Vector((0,0,24)), target, 2800, 38, (0.66,0.78,1.0))
scene.render.filepath = str(PROJECT / "audit/batch3_hovde/same_angle_reference_round13.png")
bpy.ops.render.render(write_still=True)

# Frontal portico detail from the same azimuth, with a tighter perspective frame.
focus = port + Vector((0,0,-6.0))
cam.location = focus + side*42 + Vector((0,0,0.2))
aim(cam, focus)
cam.data.lens = 50
scene.render.resolution_x, scene.render.resolution_y = 1600, 1000
scene.render.filepath = str(PROJECT / "audit/batch3_hovde/portico_detail_round13.png")
bpy.ops.render.render(write_still=True)

# Close oblique view from the side to inspect the deeper sheltered threshold,
# door/window recess and new capital foliage against the 2016 entrance photo.
focus = port + along*4 + Vector((0,0,-5.8))
cam.location = focus + side*34 + along*18 + Vector((0,0,1.5))
aim(cam, focus)
cam.data.lens = 55
scene.render.resolution_x, scene.render.resolution_y = 1500, 1000
scene.render.filepath = str(PROJECT / "audit/batch3_hovde/portico_oblique_round13.png")
bpy.ops.render.render(write_still=True)
# Oblique roof evidence from above to show the newly mapped terracotta courses.
roof_target = root.matrix_world.translation + Vector((0,0,15.4))
cam.location = roof_target + side*62 + along*14 + Vector((0,0,30))
aim(cam, roof_target)
cam.data.lens = 38
scene.render.resolution_x, scene.render.resolution_y = 1600, 1000
scene.render.filepath = str(PROJECT / "audit/batch3_hovde/roof_detail_round13.png")
bpy.ops.render.render(write_still=True)
print("Round 13 same-angle exterior, portico detail, and roof detail rendered from reopened asset.")



