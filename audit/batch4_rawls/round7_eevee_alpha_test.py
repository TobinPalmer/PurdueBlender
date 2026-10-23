import bpy, os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
m=bpy.data.materials['RAWL_CurtainWall_Glass'];m.surface_render_method='BLENDED';m.use_nodes=True
nt=m.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
for l in list(nt.links):
 if l.to_node==out and l.to_socket==out.inputs['Surface']:nt.links.remove(l)
p.inputs['Base Color'].default_value=(.48,.65,.72,1);p.inputs['Transmission Weight'].default_value=.22;p.inputs['Roughness'].default_value=.1;p.inputs['Metallic'].default_value=.05
tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=.18
nt.links.new(p.outputs['BSDF'],mix.inputs[1]);nt.links.new(tr.outputs['BSDF'],mix.inputs[2]);nt.links.new(mix.outputs['Shader'],out.inputs['Surface'])
s.render.engine='BLENDER_EEVEE';s.eevee.use_raytracing=True;s.eevee.taa_render_samples=96;s.render.resolution_x=1200;s.render.resolution_y=900
for i,(loc,power,size) in enumerate([((28,7,3.4),3500,3),((33,8,3.5),2500,3),((29,3,3.6),2000,3)]):
 ld=bpy.data.lights.new('R7_Eevee_Alpha_Fill_'+str(i),'AREA');ld.energy=power;ld.shape='DISK';ld.size=size
 lo=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(lo);lo.location=loc;lo.rotation_euler=(Vector((30,5,1))-lo.location).to_track_quat('-Z','Y').to_euler()
pane=Vector((30.576,20.79,2.4));desk=Vector((29.862,5.822,4.0));d=(desk-pane).normalized()
cd=bpy.data.cameras.new('R7_Eevee_Alpha_Test_Camera');cam=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(cam);cam.location=pane-d*3.0;cam.rotation_euler=(desk-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=38;s.camera=cam
w=bpy.data.worlds.new('R7_Alpha_Test_World');w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.58,.65,.72,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.65;s.world=w
s.render.filepath=os.path.abspath('audit/batch4_rawls/north_pane_eevee_alpha_test_high_sightline_round7.png');bpy.ops.render.render(write_still=True)
print('Eevee alpha mix test, no geometry hidden, unsaved material.')
