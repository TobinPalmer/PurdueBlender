import bpy,math
from pathlib import Path
from mathutils import Vector
D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/complete_cl50');s=bpy.context.scene
for o in s.objects:
 if o.type in {'LIGHT','CAMERA'}:o.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=32;s.view_settings.exposure=0;s.world.color=(.5,.5,.5);s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
bpy.ops.object.light_add(type='AREA',location=(-8,-10,60));bpy.context.object.data.energy=18000;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=50
bpy.ops.object.camera_add(location=(-8,-6,5.1));cam=bpy.context.object;cam.rotation_euler=(Vector((-8,13,4))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=19;s.camera=cam
bpy.ops.object.light_add(type='AREA',location=(-8,0,7.7));bpy.context.object.data.energy=1800;bpy.context.object.data.size=15
s.render.filepath=str(D/'interior.png');bpy.ops.render.render(write_still=True)

