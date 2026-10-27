"""Render a disposable exterior preview from a clean fresh asset open."""
import bpy
import math
from pathlib import Path
from mathutils import Vector

root = Path(__file__).resolve().parents[2]
asset = root / "modular" / "buildings" / "massing_phi_kappa_sigma_fid829.blend"
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene = bpy.context.scene
coll = bpy.data.collections.new("_PreviewRig_TEMP")
scene.collection.children.link(coll)

def add_area(name, loc, power, size):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = power
    data.shape = "DISK"
    data.size = size
    ob = bpy.data.objects.new(name, data)
    coll.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector((894, -198, 5.2)) - ob.location).to_track_quat("-Z", "Y").to_euler()

cam_data = bpy.data.cameras.new("_preview_camera_TEMP")
cam = bpy.data.objects.new("_preview_camera_TEMP", cam_data)
coll.objects.link(cam)
cam.location = (868, -263, 22)
cam.rotation_euler = (Vector((894, -198, 5.0)) - cam.location).to_track_quat("-Z", "Y").to_euler()
cam.data.type = "ORTHO"
cam.data.ortho_scale = 58
scene.camera = cam
add_area("_preview_key_TEMP", (852, -230, 42), 42000, 35)
add_area("_preview_fill_TEMP", (920, -150, 24), 24000, 30)
sun_data = bpy.data.lights.new("_preview_sun_TEMP", "SUN")
sun_data.energy = 2.2
sun_data.angle = math.radians(18)
sun = bpy.data.objects.new("_preview_sun_TEMP", sun_data)
coll.objects.link(sun)
sun.rotation_euler = (Vector((894, -198, 5.2)) - Vector((840, -240, 65))).to_track_quat("-Z", "Y").to_euler()
scene.world = bpy.data.worlds.new("_preview_world_TEMP")
scene.world.use_nodes = True
bg = next(n for n in scene.world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs["Color"].default_value = (0.23, 0.27, 0.32, 1)
bg.inputs["Strength"].default_value = 0.72
scene.render.engine = "BLENDER_EEVEE"
scene.eevee.taa_render_samples = 32
scene.render.resolution_x = 1100
scene.render.resolution_y = 850
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(root / "audit" / "phi_kappa_sigma" / "previews" / "phi_kappa_sigma_front.png")
scene.render.film_transparent = False
scene.view_settings.view_transform = "AgX"
scene.view_settings.exposure = 0.65
bpy.ops.render.render(write_still=True)
print("PREVIEW_FRONT", scene.render.filepath)

# Second reviewer angle exposes the rear-core step and the attached terrace/railings.
cam.location = (853, -246, 27)
cam.rotation_euler = (Vector((894, -198, 5.0)) - cam.location).to_track_quat("-Z", "Y").to_euler()
cam.data.ortho_scale = 62
scene.render.filepath = str(root / "audit" / "phi_kappa_sigma" / "previews" / "phi_kappa_sigma_roof_terrace_3q.png")
bpy.ops.render.render(write_still=True)
print("PREVIEW_TERRACE", scene.render.filepath)

cam.location = (879, -235, 20)
cam.rotation_euler = (Vector((894, -198, 5.2)) - cam.location).to_track_quat("-Z", "Y").to_euler()
cam.data.ortho_scale = 32
scene.render.resolution_x = 1400
scene.render.resolution_y = 1100
scene.render.filepath = str(root / "audit" / "phi_kappa_sigma" / "previews" / "phi_kappa_sigma_facade_detail.png")
bpy.ops.render.render(write_still=True)
print("PREVIEW_FACADE", scene.render.filepath)
