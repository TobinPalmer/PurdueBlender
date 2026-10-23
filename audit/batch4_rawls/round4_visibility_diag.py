import bpy,os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
# Diagnostic camera and illumination
cd=bpy.data.cameras.new('R4_DiagCam');cam=bpy.data.objects.new('R4_DiagCam',cd);s.collection.objects.link(cam);cam.location=(25,62,10);cam.rotation_euler=(Vector((25,20,10))-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=25;s.camera=cam
ld=bpy.data.lights.new('R4_DiagLight','AREA');ld.energy=2000;ld.size=10;l=bpy.data.objects.new('R4_DiagLight',ld);s.collection.objects.link(l);l.location=(25,55,20);l.rotation_euler=(Vector((25,20,10))-l.location).to_track_quat('-Z','Y').to_euler()
for o in s.objects:o.hide_render=o.name not in {'RAWL_North_Windows_Glass','R4_DiagCam','R4_DiagLight'}
m=bpy.data.materials.new('R4_EMISSION_DIAG');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(0.02,.5,1,1);e.inputs['Strength'].default_value=1;out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],out.inputs['Surface']);o=bpy.data.objects['RAWL_North_Windows_Glass'];o.data.materials.clear();o.data.materials.append(m)
s.render.engine='CYCLES';s.cycles.samples=8;s.render.resolution_x=1000;s.render.resolution_y=750;s.render.filepath=os.path.abspath('audit/batch4_rawls/glass_visibility_diag_round4.png');bpy.ops.render.render(write_still=True)
