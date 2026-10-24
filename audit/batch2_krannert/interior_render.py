import bpy,os
from mathutils import Vector
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=800;s.render.resolution_percentage=100
# Pulled-back eye-level view: includes the glass meeting room, open circulation,
# mixed seating and window-side work settings without a single sofa dominating.
bpy.ops.object.camera_add(location=(-18,1.0,5.8));cam=bpy.context.object;cam.rotation_euler=(Vector((-12,-2.5,5.0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=18;s.camera=cam
bpy.ops.object.light_add(type='AREA',location=(-14,-2,7.2));l=bpy.context.object;l.data.energy=1600;l.data.size=8
s.render.filepath=os.path.abspath('audit/batch2_krannert/drawingroom_r2.png');bpy.ops.render.render(write_still=True)
cam.location=(-20,-9,10.6);cam.rotation_euler=(Vector((-12,-2,9.4))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=21;l.location.z=12.0;s.render.filepath=os.path.abspath('audit/batch2_krannert/parrish_r2.png');bpy.ops.render.render(write_still=True)
