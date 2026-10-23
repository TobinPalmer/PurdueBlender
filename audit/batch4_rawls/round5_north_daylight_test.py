import bpy, os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
g=bpy.data.materials['RAWL_CurtainWall_Glass'];bs=next(n for n in g.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.45,.57,.63,1);bs.inputs['Transmission Weight'].default_value=.88;bs.inputs['Roughness'].default_value=.13;bs.inputs['Metallic'].default_value=0
if 'Coat Weight' in bs.inputs:bs.inputs['Coat Weight'].default_value=0
w=bpy.data.worlds.get('R5_Daylight_World') or bpy.data.worlds.new('R5_Daylight_World');s.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.74,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=2.2
camd=bpy.data.cameras.new('R5_Daylight_Cam');cam=bpy.data.objects.new('R5_Daylight_Cam',camd);s.collection.objects.link(cam);s.camera=cam;cam.location=(19,44,8);cam.rotation_euler=(Vector((19,20,8))-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=22
s.render.engine='CYCLES';s.cycles.samples=36;s.cycles.use_denoising=True;s.cycles.max_bounces=16;s.cycles.transmission_bounces=16;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.filepath=os.path.abspath('audit/batch4_rawls/north_daylight_depth_test_round5.png');bpy.ops.render.render(write_still=True)
