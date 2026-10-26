import bpy, math
from mathutils import Vector
s=bpy.context.scene
s.render.engine='BLENDER_EEVEE'; s.eevee.taa_render_samples=64
s.render.resolution_x=1200; s.render.resolution_y=800; s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'; s.render.filepath='//room_r4.png'
for o in bpy.data.objects:
    o.hide_render=not o.name.startswith('Tark_Dorm_')
w=s.world; w.use_nodes=True
bg=next(n for n in w.node_tree.nodes if n.type=='BACKGROUND')
bg.inputs['Color'].default_value=(0.34,0.39,0.44,1); bg.inputs['Strength'].default_value=.55
ld=bpy.data.lights.new('TarkRoom_R4_Softbox','AREA'); ld.energy=800; ld.shape='RECTANGLE'; ld.size=5; ld.size_y=3
light=bpy.data.objects.new('TarkRoom_R4_Softbox',ld); s.collection.objects.link(light); light.location=(-39,-29.5,6); light.rotation_euler=(0,0,0)
cd=bpy.data.cameras.new('TarkRoom_R4_Camera'); cd.type='ORTHO'; cd.ortho_scale=8.8; cd.clip_start=.01; cd.clip_end=100
cam=bpy.data.objects.new('TarkRoom_R4_Camera',cd); s.collection.objects.link(cam)
cam.location=(-44,-31,2.55); target=Vector((-37.2,-31,1.85)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler(); s.camera=cam
bpy.ops.render.render(write_still=True)
