import bpy,os,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
m=bpy.data.materials['RAWL_CurtainWall_Glass'];e=bpy.data.materials.new('R3_TEST_BLUE');e.use_nodes=True;nt=e.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,.2,1,1);em.inputs['Strength'].default_value=1;out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],out.inputs['Surface']);bpy.data.objects['RAWL_North_Windows_Glass'].data.materials.clear();bpy.data.objects['RAWL_North_Windows_Glass'].data.materials.append(e)
camd=bpy.data.cameras.new('testcam');cam=bpy.data.objects.new('testcam',camd);s.collection.objects.link(cam);s.camera=cam;cam.location=(25,62,10);cam.rotation_euler=(Vector((25,20,10))-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=25
s.render.engine='CYCLES';s.cycles.samples=8;s.render.resolution_x=800;s.render.resolution_y=600;s.render.filepath=os.path.abspath('audit/batch4_rawls/window_emission_fullscene_test.png');bpy.ops.render.render(write_still=True)
