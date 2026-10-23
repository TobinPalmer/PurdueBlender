import bpy,os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
keep={'RAWL_Masonry_Exterior_Walls','RAWL_North_Windows_Glass','RAWL_North_Windows_BronzeMullions','RAWL_North_Windows_LimestoneSills'}
for ob in s.objects:ob.hide_render=ob.name not in keep or ob.name=='RAWL_North_Windows_BronzeMullions'
m=bpy.data.materials.new('R4_EMIT');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(.02,.4,1,1);e.inputs['Strength'].default_value=2;out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],out.inputs['Surface']);g=bpy.data.objects['RAWL_North_Windows_Glass'];g.data.materials.clear();g.data.materials.append(m)
cd=bpy.data.cameras.new('R4_WindowCloseCam');c=bpy.data.objects.new('R4_WindowCloseCam',cd);s.collection.objects.link(c);c.location=(23,62,9);c.rotation_euler=(Vector((23,20,9))-c.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=22;s.camera=c
ld=bpy.data.lights.new('R4_WindowCloseSun','SUN');ld.energy=2;l=bpy.data.objects.new('R4_WindowCloseSun',ld);s.collection.objects.link(l);l.rotation_euler=(.4,-.5,-.8)
s.render.engine='CYCLES';s.cycles.samples=8;s.render.resolution_x=1000;s.render.resolution_y=750;s.render.filepath=os.path.abspath('audit/batch4_rawls/north_window_no_mullions_diag.png');bpy.ops.render.render(write_still=True)

