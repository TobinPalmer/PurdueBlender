import bpy,math,pathlib
from mathutils import Vector
P=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');A=P/'audit/batch3_elliott';bpy.ops.wm.open_mainfile(filepath=str(P/'modular/buildings/elliott_hall_of_music.blend'));s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1500;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.eevee.taa_render_samples=32;s.view_settings.view_transform='AgX';allow={'ELLT_B3_seat','ELLT_B3_stage','ELLT_B3_curtain','ELLT_B3_balcony'}
for o in s.objects:o.hide_render=o.name not in allow
ld=bpy.data.lights.new('TMP','AREA');ld.energy=6000;ld.shape='DISK';ld.size=20;l=bpy.data.objects.new('TMP',ld);s.collection.objects.link(l);l.location=(0,0,25)
def r(name,loc,tgt,lens):
 d=bpy.data.cameras.new(name);d.type='PERSP';d.lens=lens;c=bpy.data.objects.new(name,d);s.collection.objects.link(c);c.location=loc;c.rotation_euler=(Vector(tgt)-c.location).to_track_quat('-Z','Y').to_euler();s.camera=c;s.render.filepath=str(A/(name+'.png'));bpy.ops.render.render(write_still=True);bpy.data.objects.remove(c,do_unlink=True);bpy.data.cameras.remove(d)
r('interior_candidate_c_round8',(-15,-18,10),(13,15,6),32)
r('interior_candidate_d_round8',(25,24,13),(-8,-8,6),32)
