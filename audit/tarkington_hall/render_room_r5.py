import bpy
from mathutils import Vector
s=bpy.context.scene
s.render.engine='BLENDER_EEVEE'; s.eevee.taa_render_samples=64
s.render.resolution_x=1200; s.render.resolution_y=800; s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'; s.render.filepath='//room_r5.png'
for o in bpy.data.objects:
    o.hide_render=not o.name.startswith('Tark_Dorm_')
# Building-style cutaway: the south wall is removed only from this evidence
# render so the room layout and built-in/furniture details remain visible.
for name in ['Tark_Dorm_Room118_Wall_N','Tark_Dorm_Room118_Wall_S','Tark_Dorm_Room118_Wall_E']:
    obj=bpy.data.objects.get(name)
    if obj: obj.hide_render=True
w=s.world; w.use_nodes=True
bg=next(n for n in w.node_tree.nodes if n.type=='BACKGROUND')
bg.inputs['Color'].default_value=(0.30,0.35,0.42,1); bg.inputs['Strength'].default_value=.65
ld=bpy.data.lights.new('TarkRoom_R5_Softbox','AREA'); ld.energy=650; ld.shape='DISK'; ld.size=7
light=bpy.data.objects.new('TarkRoom_R5_Softbox',ld); s.collection.objects.link(light); light.location=(-42,-38,8); light.rotation_euler=(0,0,0)
cd=bpy.data.cameras.new('TarkRoom_R5_Camera'); cd.type='ORTHO'; cd.ortho_scale=9.2; cd.clip_start=.01; cd.clip_end=100
cam=bpy.data.objects.new('TarkRoom_R5_Camera',cd); s.collection.objects.link(cam)
cam.location=(-44,-39,7.5); target=Vector((-37.4,-31.0,1.35)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler(); s.camera=cam
bpy.ops.render.render(write_still=True)
