import bpy,os,math,json
from mathutils import Vector
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=900;s.render.resolution_y=650;s.render.resolution_percentage=100;s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.65,.7,.8,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.5
s.camera=bpy.data.objects['Cam_KRAN_02_SW_StateSt_Entrance'];s.render.filepath=os.path.abspath('audit/batch2_krannert/exterior.png');bpy.ops.render.render(write_still=True)
bpy.ops.object.camera_add(location=(-24,-8,5.5));cam=bpy.context.object;cam.rotation_euler=(Vector((-12,-2,5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=22;s.camera=cam
bpy.ops.object.light_add(type='AREA',location=(-14,-2,7.2));l=bpy.context.object;l.data.energy=1400;l.data.shape='RECTANGLE';l.data.size=10;l.data.size_y=8
s.render.filepath=os.path.abspath('audit/batch2_krannert/drawingroom.png');bpy.ops.render.render(write_still=True)
