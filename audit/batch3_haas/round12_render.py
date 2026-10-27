import bpy
from pathlib import Path
from mathutils import Vector
D=Path('audit/batch3_haas');S=bpy.context.scene;C=bpy.data.collections['Asset_felix_haas_hall']
S.render.engine='CYCLES';S.cycles.samples=24;S.cycles.use_denoising=True
S.render.resolution_x=1600;S.render.resolution_y=1280;S.render.resolution_percentage=100
S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=-1.7;S.view_settings.gamma=1.0
for name in ['HAAS_R12_QA_Key','HAAS_R12_QA_Fill','HAAS_R12_QA_Camera']:
 o=bpy.data.objects.get(name)
 if o:bpy.data.objects.remove(o,do_unlink=True)
for name,loc,energy,size,color in [('HAAS_R12_QA_Key',(60,-50,65),950,45,(1.0,.91,.79)),('HAAS_R12_QA_Fill',(-35,35,38),450,35,(.82,.9,1.0))]:
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);S.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((-6,0,5))-o.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('HAAS_R12_QA_Camera');cam=bpy.data.objects.new('HAAS_R12_QA_Camera',cd);S.collection.objects.link(cam);S.camera=cam;cd.type='ORTHO'
def render(name,loc,target,scale):
 for o in C.all_objects:
  if o:
   o.hide_render=o.name.startswith(('HAAS_Plan_','HAAS_Plan_Label_'))
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale;S.render.filepath=str((D/name).resolve());bpy.ops.render.render(write_still=True)
render('exterior_round12.png',(55,-55,38),(-6,0,6),82)
render('entrance_round12.png',(55,-32,18),(9,0,4),40)
