import bpy, os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
m=bpy.data.materials['RAWL_CurtainWall_Glass'];p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
p.inputs['Base Color'].default_value=(.84,.91,.93,1);p.inputs['Transmission Weight'].default_value=1.0;p.inputs['Roughness'].default_value=.025;p.inputs['Metallic'].default_value=0
if 'IOR' in p.inputs:p.inputs['IOR'].default_value=1.45
s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=True;s.cycles.max_bounces=24;s.cycles.transmission_bounces=16
s.render.resolution_x=1200;s.render.resolution_y=900;s.render.image_settings.file_format='PNG'
for i,(loc,power,size) in enumerate([((28,7,3.4),3500,3),((33,8,3.5),2500,3),((29,3,3.6),2000,3)]):
 ld=bpy.data.lights.new('R7_Pane_RoomFill_'+str(i),'AREA');ld.energy=power;ld.shape='DISK';ld.size=size
 lo=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(lo);lo.location=loc;lo.rotation_euler=(Vector((30,5,1))-lo.location).to_track_quat('-Z','Y').to_euler()
# Aim from outside through a measured north window pane toward the plan-room desk.
pane=Vector((30.576,20.79,2.4));desk=Vector((29.862,5.822,.795));d=(desk-pane).normalized()
cd=bpy.data.cameras.new('R7_North_Pane_Exterior_Camera');cam=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(cam);cam.location=pane-d*3.0;cam.rotation_euler=(desk-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=38;s.camera=cam
w=bpy.data.worlds.new('R7_Pane_World');w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.58,.65,.72,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.65;s.world=w
s.render.filepath=os.path.abspath('audit/batch4_rawls/north_pane_full_geometry_test_round7.png')
bpy.ops.render.render(write_still=True)
print('Full-geometry north pane test; no building objects hidden; unsaved test material and lighting.')
