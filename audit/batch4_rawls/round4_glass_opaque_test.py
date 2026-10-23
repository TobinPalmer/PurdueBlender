import bpy,os,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene;m=bpy.data.materials['RAWL_CurtainWall_Glass'];m.surface_render_method='BLENDED';bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.055,.20,.32,1);bs.inputs['Roughness'].default_value=.10;bs.inputs['Metallic'].default_value=.28;bs.inputs['Transmission Weight'].default_value=0;bs.inputs['Alpha'].default_value=1;bs.inputs['Coat Weight'].default_value=.5;bs.inputs['Coat Roughness'].default_value=.07;m.diffuse_color=(.055,.20,.32,1)
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
w=bpy.data.worlds.get('RAWL_Batch4_World') or bpy.data.worlds.new('RAWL_Batch4_World');s.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.72,.8,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
ld=bpy.data.lights.new('R4_NorthSun','SUN');ld.energy=1.7;l=bpy.data.objects.new('R4_NorthSun',ld);s.collection.objects.link(l);l.rotation_euler=(.4,-.5,-.8)
ad=bpy.data.lights.new('R4_NorthSoftbox','AREA');ad.energy=5000;ad.shape='DISK';ad.size=22;al=bpy.data.objects.new('R4_NorthSoftbox',ad);s.collection.objects.link(al);al.location=(25,48,25);al.rotation_euler=(Vector((25,20,10))-al.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('R4_NorthFrontCam');c=bpy.data.objects.new('R4_NorthFrontCam',cd);s.collection.objects.link(c);c.location=(25,64,10);c.rotation_euler=(Vector((25,20,10))-c.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=65;s.camera=c
s.render.filepath=os.path.abspath('audit/batch4_rawls/north_opaque_glass_test.png');bpy.ops.render.render(write_still=True)

