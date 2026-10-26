import bpy,math
from mathutils import Vector
s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32;s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath='//../../audit/tarkington_hall/room_r1.png'
for o in bpy.data.objects:
 if o.type in {'CAMERA','LIGHT'}:o.hide_render=True
w=s.world;w.use_nodes=True;bg=next(n for n in w.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.22,.25,.30,1);bg.inputs['Strength'].default_value=.65
ld=bpy.data.lights.new('TarkRoom_Soft','AREA');ld.energy=450;ld.shape='DISK';ld.size=4
lo=bpy.data.objects.new('TarkRoom_Soft',ld);s.collection.objects.link(lo);lo.location=(-37,-31.8,3.4);lo.rotation_euler=(math.radians(4),0,0)
cd=bpy.data.cameras.new('TarkRoom_Camera');cd.lens=24;cam=bpy.data.objects.new('TarkRoom_Camera',cd);s.collection.objects.link(cam);cam.location=(-37.4,-32.6,1.6);target=Vector((-37.3,-29.2,1.6));cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler();s.camera=cam
bpy.ops.render.render(write_still=True)
