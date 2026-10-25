import bpy
from mathutils import Vector
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/niswonger_aviation_tech_refine')
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.35;s.view_settings.gamma=1
for o in bpy.data.objects:
 if o.type=='LIGHT':o.hide_render=True
for name,loc,power,size in [('R3_Key',(-35,-10,75),8500,42),('R3_Fill',(40,42,55),4200,35)]:
 ld=bpy.data.lights.new(name,'AREA');ld.energy=power;ld.shape='DISK';ld.size=size;ob=bpy.data.objects.new(name,ld);s.collection.objects.link(ob);ob.location=loc
ca=bpy.data.cameras.new('R3_Camera');co=bpy.data.objects.new('R3_Camera',ca);s.collection.objects.link(co);s.camera=co
for name,loc,target,lens,ortho in [('exterior_r3',(75,100,57),(-7,18,3),45,None),('roofplan_r3',(0,8,125),(-7,10,2),50,105)]:
 co.location=loc;co.rotation_euler=(Vector(target)-co.location).to_track_quat('-Z','Y').to_euler();ca.lens=lens;ca.type='ORTHO' if ortho else 'PERSP'
 if ortho:ca.ortho_scale=ortho
 s.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True)
print('Rendered R3 exterior and roof plan inspection views.')
