import bpy, os
from mathutils import Vector
blend=os.path.abspath('modular/buildings/rawls_hall.blend')
bpy.ops.wm.open_mainfile(filepath=blend);s=bpy.context.scene
# Eevee does not show the old Principled transmission material clearly. Use a
# thin-pane architectural approximation: restrained tinted reflection over a
# mostly transparent surface, with blended Eevee transparency enabled.
m=bpy.data.materials['RAWL_CurtainWall_Glass'];m.use_nodes=True;m.surface_render_method='BLENDED'
nt=m.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
for l in list(nt.links):
    if l.to_node==out and l.to_socket==out.inputs['Surface']:nt.links.remove(l)
p.inputs['Base Color'].default_value=(.38,.54,.61,1);p.inputs['Transmission Weight'].default_value=.18;p.inputs['Roughness'].default_value=.09;p.inputs['Metallic'].default_value=.03
if 'IOR' in p.inputs:p.inputs['IOR'].default_value=1.45
trans=next((n for n in nt.nodes if n.type=='BSDF_TRANSPARENT'),None) or nt.nodes.new('ShaderNodeBsdfTransparent')
mix=next((n for n in nt.nodes if n.type=='MIX_SHADER'),None) or nt.nodes.new('ShaderNodeMixShader')
mix.inputs[0].default_value=.20
nt.links.new(p.outputs['BSDF'],mix.inputs[1]);nt.links.new(trans.outputs['BSDF'],mix.inputs[2]);nt.links.new(mix.outputs['Shader'],out.inputs['Surface'])
m.diffuse_color=(.38,.54,.61,.30)
s.render.engine='BLENDER_EEVEE';s.eevee.use_raytracing=True;s.eevee.ray_tracing_method='SCREEN'
s.eevee.taa_render_samples=96;s.render.film_transparent=False
bpy.ops.wm.save_as_mainfile(filepath=blend)
# Explicit reopen before verifying/rendering.
bpy.ops.wm.open_mainfile(filepath=blend);s=bpy.context.scene
for o in s.objects:o.hide_render=False
s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.filepath='//'
world=bpy.data.worlds.new('R7_Exterior_Evidence_World');world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.56,.64,.72,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45;s.world=world
# Keep the authored sun; add warm, render-only room fill so glazing reveals
# actual interiors rather than a black void. Nothing in the building is hidden.
for i,(loc,power,size,target) in enumerate([
 ((30,7,4),1600,4,(30,5,1)),((36,6,4),1400,4,(34,5,1)),((-7,-12,4),1100,4,(-8,-10,1)),
 ((18,-5,8),1200,6,(14,-5,1))]):
 ld=bpy.data.lights.new('R7_RenderOnly_InteriorFill_'+str(i),'AREA');ld.energy=power;ld.shape='DISK';ld.size=size
 lo=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(lo);lo.location=loc;lo.rotation_euler=(Vector(target)-lo.location).to_track_quat('-Z','Y').to_euler()
def render(name,eye,target,lens,res=(1200,900)):
 cd=bpy.data.cameras.new('R7_'+name+'_Camera');cam=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(cam);cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;s.camera=cam
 s.render.resolution_x,s.render.resolution_y=res;s.render.filepath=os.path.abspath('audit/batch4_rawls/'+name+'.png');bpy.ops.render.render(write_still=True);print('RENDER',name,'all building objects visible')
# Ordinary exterior view of the full building, without hidden geometry.
render('full_building_exterior_round7',(44,61,34),(9.5,-1.8,12.5),24,(1400,1000))
# Pane-level full-geometry views; the glass, frames, masonry, shell and actual
# plan-derived partitions remain visible. They intentionally show the real wall
# behind the pane where the 2024 plan puts partitions across the sightline.
render('north_pane_full_geometry_round7',(30.576,24.2,2.65),(30.576,8.0,1.9),42)
render('south_pane_full_geometry_round7',(-7.5,-27.6,2.6),(-7.5,-12.4,1.8),42)
print('Saved/reopened asset:',bpy.data.filepath,'engine:',s.render.engine,'ray tracing:',s.eevee.use_raytracing)
