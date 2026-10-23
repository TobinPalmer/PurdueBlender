import bpy,os
from mathutils import Vector
s=bpy.context.scene;cam=s.camera;P='C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch2_hicks/'
cam.location=(-9,-6,-3.65);cam.rotation_euler=(Vector((-8,5,-4.35))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=22;s.render.filepath=P+'interior.png';bpy.ops.render.render(write_still=True)
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
ld=bpy.data.lights.new('ProofSun','SUN');ld.energy=3;o=bpy.data.objects.new('ProofSun',ld);s.collection.objects.link(o);o.rotation_euler=(.3,-.4,-.5);cam.location=(36,38,27);cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=48;s.render.filepath=P+'exterior.png';bpy.ops.render.render(write_still=True)
