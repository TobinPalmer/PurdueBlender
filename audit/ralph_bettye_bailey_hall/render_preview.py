import bpy
from mathutils import Vector

scene = bpy.context.scene
obj = bpy.data.objects['Ralph & Bettye Bailey Hall']
center = Vector((308.5, -21.5, 4.0))

camera_data = bpy.data.cameras.new('BaileyPreviewCamera')
camera = bpy.data.objects.new('BaileyPreviewCamera', camera_data)
scene.collection.objects.link(camera)
camera.location = center + Vector((-52.0, -58.0, 38.0))
camera.rotation_euler = (center - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 67.0
scene.camera = camera

light_data = bpy.data.lights.new('BaileyPreviewKey', 'AREA')
light = bpy.data.objects.new('BaileyPreviewKey', light_data)
scene.collection.objects.link(light)
light.location = center + Vector((-28.0, -38.0, 44.0))
light.data.energy = 5200
light.data.shape = 'DISK'
light.data.size = 32
light.rotation_euler = (center - light.location).to_track_quat('-Z', 'Y').to_euler()

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1024
scene.render.resolution_y = 768
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.world.color = (0.12, 0.12, 0.12)
scene.view_settings.view_transform = 'AgX'
scene.render.filepath = bpy.path.abspath('//../../audit/ralph_bettye_bailey_hall/preview_detail.png')
scene.render.image_settings.color_mode = 'RGBA'
bpy.ops.render.render(write_still=True)
