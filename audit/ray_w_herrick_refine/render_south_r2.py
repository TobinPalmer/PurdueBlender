import bpy
from mathutils import Vector
s=bpy.context.scene
cam=bpy.data.objects['Preview camera']
cam.location=(0,-125,18)
target=Vector((0,0,6.5)); direction=target-Vector(cam.location)
cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'; cam.data.ortho_scale=78
s.camera=cam
s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\ray_w_herrick_refine\south_r2.png'
bpy.ops.render.render(write_still=True)

