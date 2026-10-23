import bpy,json,math
from pathlib import Path
from mathutils import Vector
D=Path('C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas');c=bpy.data.collections['Asset_felix_haas_hall'];s=bpy.context.scene
camd=bpy.data.cameras.new('Review');cam=bpy.data.objects.new('Review',camd);s.collection.objects.link(cam);s.camera=cam;camd.type='ORTHO';camd.ortho_scale=78
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100
s.world.color=(.4,.4,.4)
for name,loc,energy,size in [('Key',(0,-20,60),12000,60),('Fill',(-40,30,30),7000,40)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((-7,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
def render(name,loc,target,scale):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();camd.ortho_scale=scale;s.render.filepath=str(D/name);bpy.ops.render.render(write_still=True)
render('exterior.png',(65,-85,65),(-6,0,4),78)
for o in list(bpy.data.collections['Asset_felix_haas_hall'].all_objects):
 if o and not o.name.startswith(('HAAS_Plan_','AssetRoot')):o.hide_render=True
render('interior_plan.png',(-7,0,80),(-7,0,0),62)
render('interior_close.png',(-4,-3,17),(-10,-2,.8),23)


