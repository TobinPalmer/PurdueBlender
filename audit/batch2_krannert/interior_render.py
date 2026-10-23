import bpy,os
from mathutils import Vector
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=900;s.render.resolution_y=650;s.render.resolution_percentage=100
bpy.ops.object.camera_add(location=(-18,-7,5.5));cam=bpy.context.object;cam.rotation_euler=(Vector((-10,-.5,5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=21;s.camera=cam
bpy.ops.object.light_add(type='AREA',location=(-14,-2,7.2));l=bpy.context.object;l.data.energy=1600;l.data.size=8
s.render.filepath=os.path.abspath('audit/batch2_krannert/drawingroom.png');bpy.ops.render.render(write_still=True)
cam.location=(-18,-7,10.1);cam.rotation_euler=(Vector((-11,-2,9.4))-cam.location).to_track_quat('-Z','Y').to_euler();l.location.z=11.8;s.render.filepath=os.path.abspath('audit/batch2_krannert/parrish.png');bpy.ops.render.render(write_still=True)
