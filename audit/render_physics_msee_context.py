import bpy
import math
from pathlib import Path
from mathutils import Vector

scene = bpy.context.scene
cam_data = bpy.data.cameras.new('Audit_Physics_MSEE_Camera')
cam = bpy.data.objects.new('Audit_Physics_MSEE_Camera', cam_data)
scene.collection.objects.link(cam)
cam.location = (185.0, 105.0, 92.0)
target = Vector((48.0, 269.0, 8.0))
direction = target - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 250.0
scene.camera = cam
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.studio_light = 'paint.sl'
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = 'WORLD'
scene.render.resolution_x = 1280
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(Path(bpy.data.filepath).parent / 'audit' / 'physics_msee_master_context.png')
bpy.ops.render.render(write_still=True)
print('CONTEXT_RENDER=' + scene.render.filepath)
