import bpy,os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
m=bpy.data.materials.new('R4_EMIT_DIAG');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(0.02,.4,1,1);e.inputs['Strength'].default_value=2;out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],out.inputs['Surface']);o=bpy.data.objects['RAWL_North_Windows_Glass'];o.data.materials.clear();o.data.materials.append(m)
cd=bpy.data.cameras.new('R4_DirectCam');c=bpy.data.objects.new('R4_DirectCam',cd);s.collection.objects.link(c);c.location=(25,62,10);c.rotation_euler=(Vector((25,20,10))-c.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=30;s.camera=c
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=750
for ob in s.objects:
 if ob.type=='LIGHT':ob.hide_render=True
ld=bpy.data.lights.new('R4_DirectSun','SUN');ld.energy=2;l=bpy.data.objects.new('R4_DirectSun',ld);s.collection.objects.link(l);l.rotation_euler=(.4,-.5,-.8)
s.render.filepath=os.path.abspath('audit/batch4_rawls/north_direct_emission_diag_round4.png');bpy.ops.render.render(write_still=True)
