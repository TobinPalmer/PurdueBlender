"""Render a saved-asset preview centered on Owen Hall's documented plan."""
import bpy
from mathutils import Vector

BLEND = r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\owen_hall.blend"
OUT = r"C:\Users\Tobin\Documents\Blender\PurdueMap\audit\owen_hall_independent_grade\owen_hall_gis_footprint_topdown.png"
bpy.ops.wm.open_mainfile(filepath=BLEND)
scene = bpy.context.scene
asset = bpy.data.collections.get("Asset_owen_hall")
for obj in asset.objects:
    obj.hide_render = not obj.name.startswith("Owen_GIS_")
cam_data = bpy.data.cameras.new("Owen_Footprint_Preview_Camera")
cam = bpy.data.objects.new("Owen_Footprint_Preview_Camera", cam_data)
scene.collection.objects.link(cam)
cam_data.type = "ORTHO"
cam_data.ortho_scale = 126.0
cam.location = (-3.0, 1.8, 145.0)
cam.rotation_euler = (Vector((-3.0, 1.8, 0.0)) - cam.location).to_track_quat("-Z", "Y").to_euler()
scene.camera = cam
scene.render.filepath = OUT
scene.render.resolution_x = 1200
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
bpy.ops.render.render(write_still=True)
print(OUT)
