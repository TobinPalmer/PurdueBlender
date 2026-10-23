import bpy, os, math
from mathutils import Vector
OUT=os.path.dirname(__file__);BLEND=os.path.abspath('modular/buildings/rawls_hall.blend');bpy.ops.wm.open_mainfile(filepath=BLEND);s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=840;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
world=bpy.data.worlds.get('RAWL_Batch4_World') or bpy.data.worlds.new('RAWL_Batch4_World');s.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.52,.60,.70,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.72
for o in bpy.data.objects:
 if o.type=='LIGHT':o.hide_render=True
ld=bpy.data.lights.new('RAWL_R2_Room_Fill','AREA');ld.energy=1800;ld.shape='DISK';ld.size=10;l=bpy.data.objects.new('RAWL_R2_Room_Fill',ld);s.collection.objects.link(l);l.location=(34,-1,5);l.rotation_euler=(math.radians(75),0,0)
camd=bpy.data.cameras.new('RAWL_R2_Interior_Camera');cam=bpy.data.objects.new('RAWL_R2_Interior_Camera',camd);s.collection.objects.link(cam);s.camera=cam
def render(name,eye,target,lens=42):
 cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=lens;s.render.filepath=os.path.join(OUT,name+'.png');bpy.ops.render.render(write_still=True)
# Hide outside envelope and upper slabs for interior 1086
for o in bpy.data.objects:
 if o.name.startswith(('RAWL_Roof','RAWL_Rooftop','RAWL_Masonry_Exterior_Walls','RAWL_East_Windows','RAWL_North_Windows','RAWL_South_Windows','RAWL_West_Windows','RAWL_SE_Diagonal_CurtainWall','RAWL_NW_Rotunda')) or o.name in ['RAWL_FloorSlab_L2','RAWL_FloorSlab_L3','RAWL_FloorSlab_L4','RAWL_FloorSlab_L5']:o.hide_render=True
render('interior_1086_round2',(24,5.0,1.72),(34.0,2.3,1.52),35)
# core / room 1008 at eye level
render('interior_core_1008_round2',(-2,-14,1.72),(-5,-4,1.5),42)
# Expose atrium by removing outer walls and most facade glazing. Existing floor/column/railing geometry remains.
for o in bpy.data.objects:
 if o.name.startswith(('RAWL_Masonry_Exterior_Walls','RAWL_North_Windows','RAWL_South_Windows','RAWL_West_Windows','RAWL_East_Windows','RAWL_SE_Diagonal_CurtainWall','RAWL_NW_Rotunda','RAWL_Roof_Main_Deck','RAWL_Roof_Mechanical','RAWL_Roof_HVAC')):o.hide_render=True
render('atrium_section_round2',(11,-32,13),(11,-1,13),42)
