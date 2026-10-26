import bpy
from mathutils import Vector
s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=96
s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
w=s.world;w.use_nodes=True;bg=next(n for n in w.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.20,.25,.32,1);bg.inputs['Strength'].default_value=.5
for o in bpy.data.objects:
 n=o.name;o.hide_render=not (o.type=='MESH' and n.startswith(('Tark_Program_Standard_Double_Room','Tark_Program_Standard_Room_')) and '_Wall_' not in n and 'Door' not in n)
ld=bpy.data.lights.new('StandardRoom_Key','AREA');ld.energy=3500;ld.shape='DISK';ld.size=6;l=bpy.data.objects.new('StandardRoom_Key',ld);s.collection.objects.link(l);l.location=(-41,-42,13)
cd=bpy.data.cameras.new('StandardRoom_PlanCam');cd.type='ORTHO';cd.ortho_scale=6.7;cam=bpy.data.objects.new('StandardRoom_PlanCam',cd);s.collection.objects.link(cam);t=Vector((-41,-42,0));c=Vector((-41,-42,18));cam.location=c;cam.rotation_euler=(t-c).to_track_quat('-Z','Y').to_euler();s.camera=cam
s.render.filepath='//standard_double_room_program_r4.png';bpy.ops.render.render(write_still=True)

