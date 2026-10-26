import bpy, os
from mathutils import Vector
scene=bpy.context.scene
cx,cy=464.1726837158203,-213.28562927246094
cam_data=bpy.data.cameras.new('Granite independent end view camera')
cam=bpy.data.objects.new('Granite independent end view camera',cam_data); scene.collection.objects.link(cam)
cam.location=(cx+52,cy+48,24)
target=Vector((cx,cy,7.8)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler(); cam.data.lens=55
scene.camera=cam
scene.render.filepath=os.path.join(os.path.dirname(bpy.data.filepath),'..','..','audit','massing_granite_student_living_3732ce0','preview_end_view.png')
bpy.ops.render.render(write_still=True)
print('SECONDARY_VIEW_SAVED',scene.render.filepath)
