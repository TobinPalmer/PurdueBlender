import bpy,os,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
m=bpy.data.materials.new('R4_EMIT_VISIBLE');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(.02,.4,1,1);e.inputs['Strength'].default_value=2;out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],out.inputs['Surface']);o=bpy.data.objects['RAWL_North_Windows_Glass'];o.data.materials.clear();o.data.materials.append(m)
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=750
for x in s.objects:
 if x.type=='LIGHT':x.hide_render=True
ld=bpy.data.lights.new('R4DiagSun','SUN');ld.energy=2;l=bpy.data.objects.new('R4DiagSun',ld);s.collection.objects.link(l);l.rotation_euler=(math.radians(24),math.radians(-30),math.radians(-35))
cd=bpy.data.cameras.new('R4DiagCam');c=bpy.data.objects.new('R4DiagCam',cd);s.collection.objects.link(c);c.location=(76,73,58);c.rotation_euler=(Vector((2,0,12))-c.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=102;s.camera=c
s.render.filepath=os.path.abspath('audit/batch4_rawls/facade_emission_visibility_round4.png');bpy.ops.render.render(write_still=True)
