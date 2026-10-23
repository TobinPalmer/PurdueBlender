import bpy, os, math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
def render(name, eye, target, ortho=0, lens=55, hide=()):
 for o in s.objects:o.hide_render=False
 for n in hide:
  if n in bpy.data.objects:bpy.data.objects[n].hide_render=True
 for o in s.objects:
  if o.type=='LIGHT':o.hide_render=True
 w=bpy.data.worlds.get('RAWL_R5_Cutaway_World') or bpy.data.worlds.new('RAWL_R5_Cutaway_World');s.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.6,.68,.77,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.75
 cd=bpy.data.cameras.new('R5_'+name+'_Cam');c=bpy.data.objects.new('R5_'+name+'_Cam',cd);s.collection.objects.link(c);s.camera=c;c.location=eye;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens
 if ortho:cd.type='ORTHO';cd.ortho_scale=ortho
 else:cd.type='PERSP'
 ld=bpy.data.lights.new('R5_'+name+'_Key','AREA');ld.energy=4200;ld.shape='DISK';ld.size=18;l=bpy.data.objects.new('R5_'+name+'_Key',ld);s.collection.objects.link(l);l.location=(target[0]-10,target[1]-16,target[2]+24);l.rotation_euler=(Vector(target)-l.location).to_track_quat('-Z','Y').to_euler()
 s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.image_settings.file_format='PNG';s.render.filepath=os.path.abspath('audit/batch4_rawls/'+name+'.png');bpy.ops.render.render(write_still=True);print('RENDERED',name)
# Trial transparency is render-only here; final material value is assessed before saving.
glass=bpy.data.materials['RAWL_CurtainWall_Glass'];bs=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
bs.inputs['Transmission Weight'].default_value=.45;bs.inputs['Metallic'].default_value=.04;bs.inputs['Roughness'].default_value=.16
if 'Coat Weight' in bs.inputs:bs.inputs['Coat Weight'].default_value=.18
render('north_glazing_depth_trial_round5',(22,47,8),(22,18,8),ortho=20,hide=('RAWL_FloorSlab_L5','RAWL_Roof_Main_Deck','RAWL_Roof_Mechanical_East','RAWL_Roof_Mechanical_West','RAWL_Roof_HVAC_Units'))
# First-floor plan cutaway: reveal only the supported 2024 plan shell and modeled core/doors.
render('core_door_plan_round5',(-7,-7,38),(-7,-7,1),ortho=34,hide=('RAWL_Masonry_Exterior_Walls','RAWL_FloorSlab_L2','RAWL_FloorSlab_L3','RAWL_FloorSlab_L4','RAWL_FloorSlab_L5','RAWL_Roof_Main_Deck','RAWL_Roof_Mechanical_East','RAWL_Roof_Mechanical_West','RAWL_Roof_HVAC_Units'))
render('north_entry_cutaway_round5',(1,39,7),(1,16,1.5),ortho=26,hide=('RAWL_Masonry_Exterior_Walls','RAWL_FloorSlab_L2','RAWL_FloorSlab_L3','RAWL_FloorSlab_L4','RAWL_FloorSlab_L5','RAWL_Roof_Main_Deck','RAWL_Roof_Mechanical_East','RAWL_Roof_Mechanical_West','RAWL_Roof_HVAC_Units'))
# Atrium section view preserves existing columns, slab levels and rail geometry; cuts only the outer shell/roof.
render('atrium_section_cutaway_round5',(-7,-15,11),(10,-1,10),lens=45,hide=('RAWL_Masonry_Exterior_Walls','RAWL_Roof_Main_Deck','RAWL_Roof_Mechanical_East','RAWL_Roof_Mechanical_West','RAWL_Roof_HVAC_Units'))
