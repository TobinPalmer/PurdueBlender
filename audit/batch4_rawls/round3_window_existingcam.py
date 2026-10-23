import bpy,os
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend');s=bpy.context.scene;s.camera=bpy.data.objects['Cam_RAWL_01_North_StateSt']
m=bpy.data.materials.new('R3_Glass_VisibleTest');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(.04,.22,.38,1);e.inputs['Strength'].default_value=.45;out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],out.inputs['Surface'])
for n in ['RAWL_North_Windows_Glass']:
 o=bpy.data.objects[n];o.data.materials.clear();o.data.materials.append(m);o.location.y+=.8
s.render.engine='CYCLES';s.cycles.samples=16;s.render.resolution_x=1000;s.render.resolution_y=750;s.render.filepath=os.path.abspath('audit/batch4_rawls/facade_existing_camera_test.png');bpy.ops.render.render(write_still=True)
