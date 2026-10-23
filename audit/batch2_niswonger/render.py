import bpy,json,math
from mathutils import Vector
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch2_niswonger');c=bpy.data.collections['Asset_niswonger_aviation_tech'];s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=760;s.render.resolution_percentage=100
s.world.color=(.3,.3,.3)
# use only export plus review lighting: archived source stays hidden
for o in bpy.data.objects:
 if o.type=='LIGHT':o.hide_render=True
for loc,power,size in [((0,25,55),25000,35),((-45,60,30),15000,25)]:
 ld=bpy.data.lights.new('Review','AREA');ld.energy=power;ld.shape='DISK';ld.size=size;ob=bpy.data.objects.new('Review',ld);s.collection.objects.link(ob);ob.location=loc
ca=bpy.data.cameras.new('Review');co=bpy.data.objects.new('Review',ca);s.collection.objects.link(co);s.camera=co
views=[('exterior',(70,105,55),(-7,18,3),45),('classroom',(-14,26,2.9),(-14,17,1.5),21),('atrium',(13,41,2.2),(8,17,3.0),21)]
for name,loc,target,lens in views:
 co.location=loc;co.rotation_euler=(Vector(target)-co.location).to_track_quat('-Z','Y').to_euler();ca.lens=lens
 for o in c.all_objects:
  if o.type=='LIGHT':o.hide_render=False
 s.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True)
json.dump({'reopened':True,'export':c.name,'objects':len(c.all_objects),'missing_images':[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()]},open(P/'reopen.json','w'),indent=2)
