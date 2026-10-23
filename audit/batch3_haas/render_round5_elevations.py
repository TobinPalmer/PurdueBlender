import bpy
from pathlib import Path
from mathutils import Vector
D=Path('C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas');S=bpy.context.scene
camd=bpy.data.cameras.new('HAAS Round5 Orthographic Elevation Camera');cam=bpy.data.objects.new('HAAS Round5 Orthographic Elevation Camera',camd);S.collection.objects.link(cam);S.camera=cam;camd.type='ORTHO'
S.render.engine='CYCLES';S.cycles.samples=12;S.cycles.use_denoising=True;S.render.resolution_x=1500;S.render.resolution_y=1050;S.render.resolution_percentage=100
S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=-3.2;S.view_settings.gamma=1.0
for name,loc,energy,size in [('HAAS_R5_Key',(60,-50,65),1200,45),('HAAS_R5_Fill',(-35,35,38),600,35)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=(1,.9,.76);o=bpy.data.objects.new(name,d);S.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((-6,0,5))-o.location).to_track_quat('-Z','Y').to_euler()
for o in bpy.data.objects:
 if o.name.startswith('HAAS_Plan_'):o.hide_render=True
views=[('elevation_east.png',(70,0,19),(-5,0,5),76),('elevation_west.png',(-72,0,19),(-5,0,5),76),('elevation_south.png',(-6,-72,19),(-6,0,5),68),('elevation_north.png',(-6,72,19),(-6,0,5),68)]
for name,loc,target,scale in views:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();camd.ortho_scale=scale;S.render.filepath=str(D/name);bpy.ops.render.render(write_still=True);print('SAVED',name)
