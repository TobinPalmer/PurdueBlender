import bpy
from mathutils import Vector
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/niswonger_aviation_tech_refine')
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True
s.render.resolution_x=1050;s.render.resolution_y=760;s.render.resolution_percentage=100
for o in bpy.data.objects:
 if o.type=='LIGHT':o.hide_render=True
for name,loc,power,size in [('Refine_Key',(0,25,55),25000,35),('Refine_Fill',(-45,60,30),15000,25)]:
 ld=bpy.data.lights.new(name,'AREA');ld.energy=power;ld.shape='DISK';ld.size=size;ob=bpy.data.objects.new(name,ld);s.collection.objects.link(ob);ob.location=loc
ca=bpy.data.cameras.new('Refine_Camera');co=bpy.data.objects.new('Refine_Camera',ca);s.collection.objects.link(co);s.camera=co
co.location=(70,105,55);target=Vector((-7,18,3));co.rotation_euler=(target-co.location).to_track_quat('-Z','Y').to_euler();ca.lens=45
for o in bpy.data.collections['Asset_niswonger_aviation_tech'].all_objects:
 if o.type=='LIGHT':o.hide_render=False
s.render.filepath=str(P/'exterior_after_roof_r2.png');bpy.ops.render.render(write_still=True)
print('Rendered',s.render.filepath)
