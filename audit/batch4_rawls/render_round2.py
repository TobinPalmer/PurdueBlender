import bpy, os, math
from mathutils import Vector
OUT=os.path.dirname(__file__);BLEND=os.path.abspath('modular/buildings/rawls_hall.blend')
bpy.ops.wm.open_mainfile(filepath=BLEND);s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=840;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
world=bpy.data.worlds.get('RAWL_Batch4_World') or bpy.data.worlds.new('RAWL_Batch4_World');s.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.52,.60,.70,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.72
for o in bpy.data.objects:
 if o.type=='LIGHT':o.hide_render=True
sunD=bpy.data.lights.new('RAWL_R2_Sun','SUN');sunD.energy=2.0;sun=bpy.data.objects.new('RAWL_R2_Sun',sunD);s.collection.objects.link(sun);sun.rotation_euler=(math.radians(28),math.radians(-34),math.radians(-35))
areaD=bpy.data.lights.new('RAWL_R2_Fill','AREA');areaD.energy=1200;areaD.shape='DISK';areaD.size=18;area=bpy.data.objects.new('RAWL_R2_Fill',areaD);s.collection.objects.link(area);area.location=(18,-12,22);area.rotation_euler=(math.radians(20),0,math.radians(10))
camd=bpy.data.cameras.new('RAWL_R2_Camera');cam=bpy.data.objects.new('RAWL_R2_Camera',camd);s.collection.objects.link(cam);s.camera=cam
def render(name,eye,target,ortho=None,lens=45,res=(1200,840)):
 cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
 if ortho:cam.data.type='ORTHO';cam.data.ortho_scale=ortho
 else:cam.data.type='PERSP'
 s.render.resolution_x=res[0];s.render.resolution_y=res[1];s.render.filepath=os.path.join(OUT,name+'.png');bpy.ops.render.render(write_still=True)
# Exterior overview. Hide plan partitions/furniture only; keep facade and outer site surfaces.
vis={}
for o in bpy.data.objects:
 if o.name.startswith('RAWL_2026_'):vis[o.name]=o.hide_render;o.hide_render=True
render('exterior_round2',(76,73,58),(2,0,12),ortho=102)
for n,v in vis.items():bpy.data.objects[n].hide_render=v
# Close façade view includes the diagonal brick wall and perpendicular return at east corner.
render('brick_glazing_closeup_round2',(53,-14,10),(39,-3,10),lens=62,res=(1200,900))
# Material detail with view nearly square to the south diagonal masonry plane.
render('brick_course_detail_round2',(35,-20,8),(34,-7,8),lens=72,res=(1200,900))
# First-floor room 1086, eye level; hide roof and upper floors to avoid obstructing view.
hidden={}
for o in bpy.data.objects:
 if (o.name.startswith(('RAWL_Roof','RAWL_Rooftop')) or o.name in ['RAWL_FloorSlab_L2','RAWL_FloorSlab_L3','RAWL_FloorSlab_L4','RAWL_FloorSlab_L5'] or o.name.startswith(('RAWL_Masonry_Exterior_Walls','RAWL_East_Windows','RAWL_North_Windows','RAWL_South_Windows','RAWL_West_Windows','RAWL_SE_Diagonal_CurtainWall','RAWL_NW_Rotunda'))):hidden[o.name]=o.hide_render;o.hide_render=True
render('interior_1086_round2',(24,5.0,1.72),(34.0,2.3,1.52),lens=35)
# Core / room 1008 circulation, cut away exterior envelope to inspect plan-derived walls and door openings.
render('interior_core_1008_round2',(-2,-14,1.72),(-5,-4,1.5),lens=42)
# Atrium section view: remove the south shell and side facade, retain floors, columns, panels, rails and roof penthouse.
for o in bpy.data.objects:
 if o.name.startswith(('RAWL_Masonry_Exterior_Walls','RAWL_North_Windows','RAWL_South_Windows','RAWL_West_Windows','RAWL_East_Windows','RAWL_SE_Diagonal_CurtainWall','RAWL_NW_Rotunda','RAWL_Roof_Main_Deck','RAWL_Roof_Mechanical','RAWL_Roof_HVAC')):o.hide_render=True
render('atrium_section_round2',(11,-32,13),(11,-1,13),lens=42)
