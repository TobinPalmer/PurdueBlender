import bpy
from pathlib import Path
from mathutils import Vector
D=Path('C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas'); c=bpy.data.collections['Asset_felix_haas_hall']; s=bpy.context.scene
camd=bpy.data.cameras.new('HAAS QA Camera');cam=bpy.data.objects.new('HAAS QA Camera',camd);s.collection.objects.link(cam);s.camera=cam;camd.type='ORTHO'
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1600;s.render.resolution_y=1280;s.render.resolution_percentage=100
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-3.2;s.view_settings.gamma=1.0
for name,loc,energy,size in [('HAAS QA Key',(60,-50,65),1500,45),('HAAS QA Fill',(-35,35,38),750,35)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=(1.0,.9,.76);o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((-6,0,5))-o.location).to_track_quat('-Z','Y').to_euler()
def render(name,loc,target,scale,only_plan=False):
 for o in bpy.data.objects:
  if not any(col.name=='Asset_felix_haas_hall' for col in o.users_collection): continue
  is_plan=o.name.startswith('HAAS_Plan_') or o.name.startswith('HAAS_Plan_Label_')
  o.hide_render=(not is_plan if only_plan else is_plan)
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();camd.ortho_scale=scale;s.render.filepath=str(D/name);bpy.ops.render.render(write_still=True)
render('exterior_final.png',(55,-55,38),(-6,0,6),82)
render('interior_plan_final.png',(-6,0,90),(-6,0,0),70,True)
render('entrance_final.png',(55,-32,18),(9,0,4),40)
