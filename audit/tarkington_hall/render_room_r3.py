import bpy,math
from mathutils import Vector
s=bpy.context.scene
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32;s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath='//../../audit/tarkington_hall/room_r3.png'
for o in bpy.data.objects:
 if o.type in {'CAMERA','LIGHT'}:o.hide_render=True
w=s.world;w.use_nodes=True;bg=next(n for n in w.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.22,.25,.30,1);bg.inputs['Strength'].default_value=.65
ld=bpy.data.lights.new('TarkRoom_Soft','AREA');ld.energy=450;ld.shape='DISK';ld.size=4
lo=bpy.data.objects.new('TarkRoom_Soft',ld);s.collection.objects.link(lo);lo.location=(-37,-31.8,3.4);lo.rotation_euler=(0,0,0)
cd=bpy.data.cameras.new('TarkRoom_Camera');cd.type='ORTHO';cd.ortho_scale=8;cd.clip_start=.01;cd.clip_end=100
cam=bpy.data.objects.new('TarkRoom_Camera',cd);s.collection.objects.link(cam);cam.location=(-38,-32.8,1.6);target=Vector((-37,-29.5,1.7));cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler();s.camera=cam
D=s.eevee
print('camera',tuple(cam.location),tuple(cam.rotation_euler),'dir',tuple(cam.matrix_world.to_3x3()@Vector((0,0,-1))))
for o in ['Tark_Dorm_Room118_Floor','Tark_Dorm_Room118_Wall_E','Tark_Dorm_Bed_Frame_0']:
 x=bpy.data.objects[o];print(o,x.hide_render,tuple(x.matrix_world.translation))
# render close cutaway by moving the camera slightly outside the south room wall, into the room
bpy.ops.render.render(write_still=True)

