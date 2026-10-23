import bpy, os, math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
def hide_all_except(predicate):
 for o in s.objects:o.hide_render=not predicate(o)
def camera(name,eye,target,ortho=0,lens=55):
 d=bpy.data.cameras.new(name);c=bpy.data.objects.new(name,d);s.collection.objects.link(c);s.camera=c;c.location=eye;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();d.lens=lens
 if ortho:d.type='ORTHO';d.ortho_scale=ortho
 else:d.type='PERSP'
 return c
def light(name,loc,target,power,size,hidden_camera=False):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 try:o.visible_camera=not hidden_camera
 except:pass
 return o
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
w=bpy.data.worlds.get('RAWL_R5_FinalEvidence') or bpy.data.worlds.new('RAWL_R5_FinalEvidence');s.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.68,.74,.8,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True;s.cycles.max_bounces=16;s.cycles.transmission_bounces=16;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.image_settings.file_format='PNG'
# North glazing trial: clear enough to reveal modeled depth while keeping a cool architectural tint.
g=bpy.data.materials['RAWL_CurtainWall_Glass'];bs=next(n for n in g.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.22,.36,.43,1);bs.inputs['Transmission Weight'].default_value=.82;bs.inputs['Roughness'].default_value=.10;bs.inputs['Metallic'].default_value=0
if 'Coat Weight' in bs.inputs:bs.inputs['Coat Weight'].default_value=.10
hide_all_except(lambda o:True)
camera('R5_North_Depth_Camera',(22,48,8),(22,18,8),20)
light('R5_Interior_Fill',(22,17,8),(22,21,8),650,12,True)
s.render.filepath=os.path.abspath('audit/batch4_rawls/north_interior_depth_cutaway_round5.png');bpy.ops.render.render(write_still=True)
# Source-supported first-floor core partitions/door openings only; top-down view remains legible without the opaque floor slab.
hide_all_except(lambda o:any(k in o.name for k in ['PlanCore','PlanCoreDivider','NorthStair']) or o.name=='RAWL_North_Entrance_Doors')
camera('R5_Core_Plan_Camera',(-8,-10,34),(-8,-10,1),24)
light('R5_Core_Plan_Fill',(-8,-10,22),(-8,-10,0),1800,22,True)
s.render.filepath=os.path.abspath('audit/batch4_rawls/core_partitions_plan_round5.png');bpy.ops.render.render(write_still=True)
# Existing atrium columns and approximate evidence-informed railwork only; no unsupported bridges/stairs are shown.
hide_all_except(lambda o:o.name in ['RAWL_Atrium_Structural_Columns','RAWL_R2_Atrium_Railwork_EvidenceInformed'])
camera('R5_Atrium_Structure_Camera',(-11,-14,12),(10,-1,11),lens=45)
light('R5_Atrium_Structure_Fill',(-6,-10,30),(10,-1,11),2600,20,True)
s.render.filepath=os.path.abspath('audit/batch4_rawls/atrium_columns_railwork_round5.png');bpy.ops.render.render(write_still=True)
