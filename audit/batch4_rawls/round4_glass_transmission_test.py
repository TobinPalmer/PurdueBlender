import bpy,os,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
m=bpy.data.materials['RAWL_CurtainWall_Glass'];m.use_nodes=True;bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.28,.45,.55,1);bs.inputs['Roughness'].default_value=.06;bs.inputs['Metallic'].default_value=.0;bs.inputs['Transmission Weight'].default_value=.72;bs.inputs['Alpha'].default_value=1;bs.inputs['IOR'].default_value=1.45
camd=bpy.data.cameras.new('R4_FrontTestCam');cam=bpy.data.objects.new('R4_FrontTestCam',camd);s.collection.objects.link(cam);s.camera=cam;cam.location=(25,62,10);cam.rotation_euler=(Vector((25,20,10))-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=25
s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.filepath=os.path.abspath('audit/batch4_rawls/facade_high_transmission_test_round4.png')
# make the measured glass test view evenly lit
w=bpy.data.worlds.new('R4_FrontTestWorld');w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.75,.80,.84,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.6;s.world=w
ld=bpy.data.lights.new('R4_FrontTestArea','AREA');ld.energy=1800;ld.shape='DISK';ld.size=12;l=bpy.data.objects.new('R4_FrontTestArea',ld);s.collection.objects.link(l);l.location=(18,50,22);l.rotation_euler=(Vector((25,20,10))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.render.render(write_still=True)
