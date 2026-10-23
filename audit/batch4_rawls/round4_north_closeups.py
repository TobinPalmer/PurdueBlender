import bpy,os,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=750;s.render.image_settings.file_format='PNG'
w=bpy.data.worlds.get('RAWL_Batch4_World') or bpy.data.worlds.new('RAWL_Batch4_World');s.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.55,.64,.75,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
for o in bpy.data.objects:
 if o.type=='LIGHT':o.hide_render=True
ld=bpy.data.lights.new('R4_NorthClose_Sun','SUN');ld.energy=2.2;sun=bpy.data.objects.new('R4_NorthClose_Sun',ld);s.collection.objects.link(sun);sun.rotation_euler=(math.radians(24),math.radians(-30),math.radians(-35))
ad=bpy.data.lights.new('R4_NorthClose_Softbox','AREA');ad.energy=4000;ad.shape='DISK';ad.size=14;area=bpy.data.objects.new('R4_NorthClose_Softbox',ad);s.collection.objects.link(area);area.location=(25,52,18);area.rotation_euler=(Vector((25,20,11))-area.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('R4_NorthClose_Camera');c=bpy.data.objects.new('R4_NorthClose_Camera',cd);s.collection.objects.link(c);s.camera=c
for name,eye,target,lens in [('north_glazing_closeup_round4',(25,61,11),(25,20,11),55),('north_glazing_oblique_round4',(35,58,12),(20,20,11),55)]:
 c.location=eye;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='PERSP';c.data.lens=lens;s.render.filepath=os.path.abspath('audit/batch4_rawls/'+name+'.png');bpy.ops.render.render(write_still=True)
