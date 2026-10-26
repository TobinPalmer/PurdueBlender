import bpy,os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
# clean, repeatable small area fill placed only in evidence session
ld=bpy.data.lights.new('R8_South_Aperture_Fill','AREA');ld.energy=900;ld.shape='DISK';ld.size=5;o=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(o);o.location=(-8,-17,7);o.rotation_euler=(Vector((-8,-24,7))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('R8_South_Aperture_Camera');c=bpy.data.objects.new(d.name,d);s.collection.objects.link(c);c.location=(-8,-37,10);c.rotation_euler=(Vector((-8,-23,9))-c.location).to_track_quat('-Z','Y').to_euler();d.lens=52;s.camera=c;s.render.filepath=os.path.abspath('audit/batch4_rawls/south_aperture_detail_round8.png');bpy.ops.render.render(write_still=True)
