import bpy, os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
def prep(name,eye,target,ortho,hide):
 for o in s.objects:o.hide_render=False
 for n in hide:
  if n in bpy.data.objects:bpy.data.objects[n].hide_render=True
 for o in s.objects:
  if o.type=='LIGHT':o.hide_render=True
 w=bpy.data.worlds.get('RAWL_R5_ViewWorld') or bpy.data.worlds.new('RAWL_R5_ViewWorld');s.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.7,.74,.78,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
 cd=bpy.data.cameras.new('R5_'+name+'_Camera');c=bpy.data.objects.new('R5_'+name+'_Camera',cd);s.collection.objects.link(c);s.camera=c;c.location=eye;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=ortho
 key=bpy.data.lights.new('R5_'+name+'_Key','AREA');key.energy=5000;key.shape='DISK';key.size=20;ko=bpy.data.objects.new('R5_'+name+'_Key',key);s.collection.objects.link(ko);ko.location=(target[0]-10,target[1]-12,target[2]+25);ko.rotation_euler=(Vector(target)-ko.location).to_track_quat('-Z','Y').to_euler()
 s.render.engine='CYCLES';s.cycles.samples=40;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.image_settings.file_format='PNG'
 return c
# Show actual depth through a single north bay: high transmission plus restrained inside fill, all temporary for this evidence test.
g=bpy.data.materials['RAWL_CurtainWall_Glass'];bs=next(n for n in g.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.48,.65,.73,1);bs.inputs['Transmission Weight'].default_value=.82;bs.inputs['Roughness'].default_value=.08;bs.inputs['Metallic'].default_value=.0
if 'Coat Weight' in bs.inputs:bs.inputs['Coat Weight'].default_value=.06
for o in s.objects:o.hide_render=False
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
c=prep('north_transparent_depth_round5',(22,46,8),(22,19,8),20,())
light=bpy.data.lights.new('R5_Interior_Fill','AREA');light.energy=1800;light.shape='DISK';light.size=5;lo=bpy.data.objects.new('R5_Interior_Fill',light);s.collection.objects.link(lo);lo.location=(22,16,8);lo.rotation_euler=(Vector((22,21,8))-lo.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=os.path.abspath('audit/batch4_rawls/north_transparent_depth_trial_round5.png');bpy.ops.render.render(write_still=True)
# Clean top-down plan of supported first-floor partition/core geometry; hide the opaque floor slab as well as upper shell.
c=prep('core_door_clean_plan_round5',(-8,-10,38),(-8,-10,1),26,('RAWL_Masonry_Exterior_Walls','RAWL_FloorSlab_L1_Ground','RAWL_FloorSlab_L2','RAWL_FloorSlab_L3','RAWL_FloorSlab_L4','RAWL_FloorSlab_L5','RAWL_Roof_Main_Deck','RAWL_Roof_Mechanical_East','RAWL_Roof_Mechanical_West','RAWL_Roof_HVAC_Units'))
s.render.filepath=os.path.abspath('audit/batch4_rawls/core_door_clean_plan_round5.png');bpy.ops.render.render(write_still=True)
# Simplified atrium section: expose source-supported columns and railwork without invented stairs/bridges.
c=prep('atrium_structure_section_round5',(-9,-15,12),(10,-1,11),32,('RAWL_Masonry_Exterior_Walls','RAWL_FloorSlab_L1_Ground','RAWL_FloorSlab_L2','RAWL_FloorSlab_L3','RAWL_FloorSlab_L4','RAWL_FloorSlab_L5','RAWL_Roof_Main_Deck','RAWL_Roof_Mechanical_East','RAWL_Roof_Mechanical_West','RAWL_Roof_HVAC_Units','RAWL_Atrium_Mezzanine_Balustrades'))
s.render.filepath=os.path.abspath('audit/batch4_rawls/atrium_structure_section_round5.png');bpy.ops.render.render(write_still=True)
