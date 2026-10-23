import bpy, os, json
from mathutils import Vector
blend=os.path.abspath('modular/buildings/rawls_hall.blend')
bpy.ops.wm.open_mainfile(filepath=blend)
# Lower active brick mortar contrast without changing the measured brick/course scale.
brick=bpy.data.materials['RAWL_Purdue_Red_Brick'];pr=next(n for n in brick.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
active=next(l.from_node for l in pr.inputs['Base Color'].links if l.from_node.type=='TEX_BRICK')
active.inputs['Mortar'].default_value=(.29,.235,.19,1);active.inputs['Mortar Size'].default_value=.0045
# Modestly increase clarity/transmission while retaining a cool tinted architectural glazing finish.
glass=bpy.data.materials['RAWL_CurtainWall_Glass'];gs=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
gs.inputs['Base Color'].default_value=(.18,.30,.37,1);gs.inputs['Transmission Weight'].default_value=.40;gs.inputs['Roughness'].default_value=.14;gs.inputs['Metallic'].default_value=.03
if 'Coat Weight' in gs.inputs:gs.inputs['Coat Weight'].default_value=.12
if 'IOR' in gs.inputs:gs.inputs['IOR'].default_value=1.45
glass.diffuse_color=(.18,.30,.37,1)
bpy.ops.wm.save_as_mainfile(filepath=blend)
changes={'saved_asset':blend,'brick':{'active_texture_node':active.name,'mortar_color':[.29,.235,.19,1],'mortar_size':.0045,'brick_width_m':active.inputs['Brick Width'].default_value,'course_height_m':active.inputs['Row Height'].default_value},'glass':{'base_color':[.18,.30,.37,1],'transmission':.40,'roughness':.14,'metallic':.03,'ior':1.45},'render_only_cutaway':{'hidden_source_supported_partitions':['RAWL_2026_PlanNWVestibule_03_00','RAWL_2026_PlanNWVestibule_01_01','RAWL_2026_Plan1086_04_00'],'note':'Hidden only for the illustrative through-pane sightline render; these walls remain saved in the model.'}}
with open('audit/batch4_rawls/round6_model_changes.json','w') as f:json.dump(changes,f,indent=2)
# Fresh reopen before all round6 evidence renders.
bpy.ops.wm.open_mainfile(filepath=blend);s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
print('REOPENED',bpy.data.filepath,'collection_objects',len(bpy.data.collections['Asset_rawls_hall'].all_objects),'wall_faces',len(bpy.data.objects['RAWL_Masonry_Exterior_Walls'].data.polygons))
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
w=bpy.data.worlds.new('R6_Evidence_World');w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.62,.69,.76,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.75;s.world=w
s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True;s.cycles.max_bounces=20;s.cycles.transmission_bounces=16;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.image_settings.file_format='PNG'
def render_camera(name,eye,target,lens,hide_names=()):
 for o in s.objects:o.hide_render=False
 for n in hide_names:
  if n in bpy.data.objects:bpy.data.objects[n].hide_render=True
 for o in s.objects:
  if o.type=='LIGHT':o.hide_render=True
 cd=bpy.data.cameras.new('R6_'+name+'_Camera');cam=bpy.data.objects.new('R6_'+name+'_Camera',cd);s.collection.objects.link(cam);s.camera=cam;cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='PERSP';cd.lens=lens
 ld=bpy.data.lights.new('R6_'+name+'_Key','AREA');ld.energy=1300;ld.shape='DISK';ld.size=12;lo=bpy.data.objects.new('R6_'+name+'_Key',ld);s.collection.objects.link(lo);lo.location=(target[0]+10,target[1]-2,target[2]+12);lo.rotation_euler=(Vector(target)-lo.location).to_track_quat('-Z','Y').to_euler()
 s.render.filepath=os.path.abspath('audit/batch4_rawls/'+name+'.png');bpy.ops.render.render(write_still=True);print('RENDERED',name)
# Representative room sightline. Camera is aligned to an existing north pane center and a desk in the plan-derived 1086 classroom.
pane=Vector((20.03,20.675,2.4));desk=Vector((29.862,5.822,.795));direction=(desk-pane).normalized();eye=pane-direction*3.5
render_camera('north_1086_room_sightline_cutaway_round6',eye,desk,40,('RAWL_2026_PlanNWVestibule_03_00','RAWL_2026_PlanNWVestibule_01_01','RAWL_2026_Plan1086_04_00'))
# Brick closeup after the mortar adjustment, keeping the saved mapping and course scale.
render_camera('brick_mortar_closeup_round6',(-8,-33,10),(-8,-24.4,10),55)
# A clean atrium structural view without the obstructing foreground slab; only saved columns and saved railwork are visible.
keep={'RAWL_Atrium_Structural_Columns','RAWL_R2_Atrium_Railwork_EvidenceInformed'}
for o in s.objects:o.hide_render=o.name not in keep
cd=bpy.data.cameras.new('R6_Atrium_Void_Camera');cam=bpy.data.objects.new('R6_Atrium_Void_Camera',cd);s.collection.objects.link(cam);s.camera=cam;cam.location=(-10,-16,11);cam.rotation_euler=(Vector((10,-1,11))-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='PERSP';cd.lens=42
ld=bpy.data.lights.new('R6_Atrium_Void_Fill','AREA');ld.energy=2600;ld.size=20;lo=bpy.data.objects.new('R6_Atrium_Void_Fill',ld);s.collection.objects.link(lo);lo.location=(-6,-10,30);lo.rotation_euler=(Vector((10,-1,11))-lo.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=os.path.abspath('audit/batch4_rawls/atrium_void_clear_section_round6.png');bpy.ops.render.render(write_still=True);print('RENDERED atrium_void_clear_section_round6')
