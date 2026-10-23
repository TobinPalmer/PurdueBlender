import bpy,os,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
for o in bpy.data.objects:o.hide_render=True
names=('RAWL_Masonry_Exterior_Walls','RAWL_North_Windows_Glass','RAWL_North_Windows_BronzeMullions','RAWL_North_Windows_LimestoneSills')
for o in bpy.data.objects:
 if o.name.startswith(names):o.hide_render=False
m=bpy.data.materials['RAWL_CurtainWall_Glass'];m.use_nodes=True;nt=m.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.12,.24,.31,1);bs.inputs['Roughness'].default_value=.24;bs.inputs['Metallic'].default_value=.22;bs.inputs['Transmission Weight'].default_value=0
if 'Emission Color' in bs.inputs:bs.inputs['Emission Color'].default_value=(.12,.23,.30,1);bs.inputs['Emission Strength'].default_value=.16
m.diffuse_color=(.12,.24,.31,1)
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900
s.world=bpy.data.worlds.new('R3_Facade_World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.55,.62,.70,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.75
ld=bpy.data.lights.new('R3_Facade_Area','AREA');ld.energy=3500;ld.shape='DISK';ld.size=14;l=bpy.data.objects.new('R3_Facade_Area',ld);s.collection.objects.link(l);l.location=(24,42,19);l.rotation_euler=(Vector((24,20,10))-l.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('R3_Facade_Camera');cam=bpy.data.objects.new('R3_Facade_Camera',camd);s.collection.objects.link(cam);s.camera=cam;cam.location=(25,62,10);cam.rotation_euler=(Vector((25,20,10))-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=25
s.render.filepath=os.path.abspath('audit/batch4_rawls/facade_glazing_test_round3.png');bpy.ops.render.render(write_still=True)
