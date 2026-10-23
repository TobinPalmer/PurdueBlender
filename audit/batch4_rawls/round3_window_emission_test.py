import bpy,os,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
for o in bpy.data.objects:o.hide_render=True
for n in ['RAWL_North_Windows_Glass','RAWL_North_Windows_BronzeMullions']:
 o=bpy.data.objects[n];o.hide_render=False;o.location.y+=1.5
m=bpy.data.materials.new('R3_TEST_EMISSION');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(0,0.2,1,1);e.inputs['Strength'].default_value=1;out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],out.inputs['Surface'])
bpy.data.objects['RAWL_North_Windows_Glass'].data.materials.clear();bpy.data.objects['RAWL_North_Windows_Glass'].data.materials.append(m)
camd=bpy.data.cameras.new('testcam');cam=bpy.data.objects.new('testcam',camd);s.collection.objects.link(cam);s.camera=cam;cam.location=(25,62,10);cam.rotation_euler=(Vector((25,20,10))-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=25
s.render.engine='CYCLES';s.cycles.samples=8;s.render.resolution_x=800;s.render.resolution_y=600;s.render.filepath=os.path.abspath('audit/batch4_rawls/window_emission_test.png');bpy.ops.render.render(write_still=True)
