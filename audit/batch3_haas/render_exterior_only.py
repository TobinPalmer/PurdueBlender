import bpy
from pathlib import Path
from mathutils import Vector
D=Path('C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas');c=bpy.data.collections['Asset_felix_haas_hall'];s=bpy.context.scene
camd=bpy.data.cameras.new('HAAS QA Exterior');cam=bpy.data.objects.new('HAAS QA Exterior',camd);s.collection.objects.link(cam);s.camera=cam;camd.type='ORTHO'
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=1600;s.render.resolution_y=1280;s.render.resolution_percentage=100
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-3.2;s.view_settings.gamma=1.0
for name,loc,energy,size in [('HAAS QA Key Exterior',(60,-50,65),1200,45),('HAAS QA Fill Exterior',(-35,35,38),600,35)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=(1,.9,.76);o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((-6,0,5))-o.location).to_track_quat('-Z','Y').to_euler()
for o in bpy.data.objects:
 if any(col.name=='Asset_felix_haas_hall' for col in o.users_collection) and o.name.startswith('HAAS_Plan_'):o.hide_render=True
cam.location=(55,-55,38);cam.rotation_euler=(Vector((-6,0,6))-cam.location).to_track_quat('-Z','Y').to_euler();camd.ortho_scale=82;s.render.filepath=str(D/'exterior_final.png');bpy.ops.render.render(write_still=True)
