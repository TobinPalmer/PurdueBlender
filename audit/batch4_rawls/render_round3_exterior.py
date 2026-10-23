import bpy,math,os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
w=bpy.data.worlds.get('RAWL_Batch4_World') or bpy.data.worlds.new('RAWL_Batch4_World');s.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.55,.64,.75,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
for o in bpy.data.objects:
 if o.type=='LIGHT':o.hide_render=True
ld=bpy.data.lights.new('R3_Corner_Sun','SUN');ld.energy=2.2;o=bpy.data.objects.new('R3_Corner_Sun',ld);s.collection.objects.link(o);o.rotation_euler=(math.radians(24),math.radians(-30),math.radians(-35))
d=bpy.data.cameras.new('R3_Exterior_Camera');c=bpy.data.objects.new('R3_Exterior_Camera',d);s.collection.objects.link(c);s.camera=c
for name,eye,target,lens in [('exterior_round3',(76,73,58),(2,0,12),None),('brick_glazing_closeup_round3',(53,-14,10),(39,-3,10),62),('brick_course_detail_round3',(35,-20,8),(34,-7,8),72)]:
 c.location=eye;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler()
 if lens is None:c.data.type='ORTHO';c.data.ortho_scale=102
 else:c.data.type='PERSP';c.data.lens=lens
 s.render.filepath=os.path.abspath('audit/batch4_rawls/'+name+'.png');bpy.ops.render.render(write_still=True)
