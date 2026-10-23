import bpy,math
from pathlib import Path
from mathutils import Vector
D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_cl50');s=bpy.context.scene
for o in s.objects:
 if o.type in {'LIGHT','CAMERA'}:o.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=32;s.view_settings.exposure=-3;s.world.color=(.5,.5,.5);s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
bpy.ops.object.light_add(type='AREA',location=(-8,-10,60));bpy.context.object.data.energy=18000;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=50
bpy.ops.object.camera_add(location=(50,-70,48));cam=bpy.context.object;cam.rotation_euler=(Vector((-8,0,6))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=65;s.camera=cam;s.render.filepath=str(D/'exterior.png');bpy.ops.render.render(write_still=True)
for o in bpy.data.collections['Asset_class_of_1950'].all_objects:
 if o and any(t in o.name for t in ['GIS','Penthouse','AcousticTile']):o.hide_render=True
cam.location=(-8,-60,65);cam.rotation_euler=(Vector((-8,0,1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=55;s.render.filepath=str(D/'cutaway.png');bpy.ops.render.render(write_still=True)



