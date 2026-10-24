import bpy
from mathutils import Vector

ASSET = r"modular/buildings/life_science_plant_and_soils_laboratory.blend"
OUT = r"C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batchC_life_science_plant_soils\exterior_west_r2.png"
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene = bpy.context.scene
cam = next((o for o in bpy.data.objects if o.type == 'CAMERA'), None)
if cam is None:
    data = bpy.data.cameras.new('LSPS west review camera')
    cam = bpy.data.objects.new('LSPS west review camera', data)
    scene.collection.objects.link(cam)
cam.location = Vector((-100, 0, 27))
target = Vector((0, 0, 5.2))
direction = target - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 83
scene.camera = cam
scene.render.resolution_x = 1200
scene.render.resolution_y = 780
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = OUT
scene.world.color = (0.16, 0.20, 0.25)
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'Medium High Contrast'
scene.view_settings.exposure = 0.35
scene.view_settings.gamma = 1.0
for obj in bpy.data.objects:
    if obj.type == 'LIGHT' and 'Preview' in obj.name:
        obj.data.energy = max(1100, obj.data.energy)
bpy.ops.render.render(write_still=True)
print('RENDERED', OUT)
