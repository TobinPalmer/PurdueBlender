import bpy,os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
o=bpy.data.objects['RAWL_North_Windows_Glass'];m=bpy.data.materials.new('R4_EMIT');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(.02,.4,1,1);e.inputs['Strength'].default_value=3;out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],out.inputs['Surface']);o.data.materials.clear();o.data.materials.append(m)
cd=bpy.data.cameras.new('R4_NorthEmissionCam');c=bpy.data.objects.new('R4_NorthEmissionCam',cd);s.collection.objects.link(c);c.location=(25,64,10);c.rotation_euler=(Vector((25,20,10))-c.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=65;s.camera=c
s.render.engine='CYCLES';s.cycles.samples=8;s.render.resolution_x=1200;s.render.resolution_y=800;s.render.filepath=os.path.abspath('audit/batch4_rawls/north_emission_after_rebuild.png');bpy.ops.render.render(write_still=True)
