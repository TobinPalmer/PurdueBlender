import bpy,os,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
m=bpy.data.materials['RAWL_CurtainWall_Glass'];m.use_nodes=True;bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
bs.inputs['Base Color'].default_value=(.08,.28,.42,1);bs.inputs['Roughness'].default_value=.11;bs.inputs['Metallic'].default_value=.32;bs.inputs['Transmission Weight'].default_value=.0;bs.inputs['IOR'].default_value=1.45
if 'Coat Weight' in bs.inputs:bs.inputs['Coat Weight'].default_value=.5;bs.inputs['Coat Roughness'].default_value=.08
if 'Emission Strength' in bs.inputs:bs.inputs['Emission Strength'].default_value=0
m.diffuse_color=(.08,.28,.42,1)
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900
w=bpy.data.worlds.get('RAWL_Batch4_World') or bpy.data.worlds.new('RAWL_Batch4_World');s.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.55,.64,.75,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
for o in bpy.data.objects:
 if o.type=='LIGHT':o.hide_render=True
ld=bpy.data.lights.new('R4_MatTest_Sun','SUN');ld.energy=2.2;o=bpy.data.objects.new('R4_MatTest_Sun',ld);s.collection.objects.link(o);o.rotation_euler=(math.radians(24),math.radians(-30),math.radians(-35))
ad=bpy.data.lights.new('R4_MatTest_Area','AREA');ad.energy=4500;ad.shape='DISK';ad.size=28;al=bpy.data.objects.new('R4_MatTest_Area',ad);s.collection.objects.link(al);al.location=(30,55,32);al.rotation_euler=(Vector((0,0,12))-al.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('R4_MatTestCam');c=bpy.data.objects.new('R4_MatTestCam',d);s.collection.objects.link(c);s.camera=c
for name,eye,target,lens in [('glassmetal_exterior_test',(76,73,58),(2,0,12),None),('glassmetal_closeup_test',(53,-14,10),(39,-3,10),62)]:
 c.location=eye;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler()
 if lens is None:c.data.type='ORTHO';c.data.ortho_scale=102
 else:c.data.type='PERSP';c.data.lens=lens
 s.render.filepath=os.path.abspath('audit/batch4_rawls/'+name+'.png');bpy.ops.render.render(write_still=True)
