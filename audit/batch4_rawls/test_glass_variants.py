import bpy,math,os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene;g=bpy.data.materials['RAWL_CurtainWall_Glass'];bs=next(n for n in g.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=700;s.render.resolution_y=525;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
w=bpy.data.worlds.new('R2_Glass_Test_World');s.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.6,.68,.8,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=1.2
for o in bpy.data.objects:
 if o.type=='LIGHT':o.hide_render=True
ld=bpy.data.lights.new('R2_Glass_Test_Sun','SUN');ld.energy=3;o=bpy.data.objects.new('R2_Glass_Test_Sun',ld);s.collection.objects.link(o);o.rotation_euler=(math.radians(20),math.radians(-30),math.radians(-35))
cD=bpy.data.cameras.new('R2_Glass_Test_Camera');c=bpy.data.objects.new('R2_Glass_Test_Camera',cD);s.collection.objects.link(c);s.camera=c
for name,color,trans,metal,rough in [('glass_test_a',(0.70,.82,.88,1),.75,0,.12),('glass_test_b',(0.45,.58,.65,1),.40,.1,.18),('glass_test_c',(.30,.42,.50,1),.08,.35,.17)]:
 bs.inputs['Base Color'].default_value=color;bs.inputs['Transmission Weight'].default_value=trans;bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 c.location=(53,-14,10);c.rotation_euler=(Vector((39,-3,10))-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=62
 s.render.filepath=os.path.abspath('audit/batch4_rawls/'+name+'.png');bpy.ops.render.render(write_still=True)
