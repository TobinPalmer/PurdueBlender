import bpy,os,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
m=bpy.data.materials.new('DEBUG_Neon_Glass');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(0,0.2,1,1);e.inputs['Strength'].default_value=1;out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],out.inputs['Surface']);bpy.data.objects['RAWL_North_Windows_Glass'].data.materials.clear();bpy.data.objects['RAWL_North_Windows_Glass'].data.materials.append(m)
s.render.engine='CYCLES';s.cycles.samples=8;s.render.resolution_x=1000;s.render.resolution_y=750
ld=bpy.data.lights.new('debugSun','SUN');ld.energy=2.2;o=bpy.data.objects.new('debugSun',ld);s.collection.objects.link(o);o.rotation_euler=(math.radians(24),math.radians(-30),math.radians(-35))
d=bpy.data.cameras.new('debugcam');c=bpy.data.objects.new('debugcam',d);s.collection.objects.link(c);s.camera=c;c.location=(76,73,58);c.rotation_euler=(Vector((2,0,12))-c.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=102
s.render.filepath=os.path.abspath('audit/batch4_rawls/north_glass_neon_hero_test.png');bpy.ops.render.render(write_still=True)
