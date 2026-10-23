import bpy
from mathutils import Vector
p='modular/buildings/knoy_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
sc=bpy.context.scene
camd=bpy.data.cameras.new('AuditBrickClose')
cam=bpy.data.objects.new('AuditBrickClose',camd); sc.collection.objects.link(cam)
cam.location=(0,-62,8); target=Vector((0,-45,8)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); camd.lens=70; camd.sensor_width=36
sc.camera=cam; sc.render.resolution_x=1400; sc.render.resolution_y=900; sc.render.resolution_percentage=100
sc.render.filepath='C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_knoy/knoy_brick_texture_closeup.png'
bpy.ops.render.render(write_still=True)

