import bpy,os,math
from mathutils import Vector
OUT=os.path.dirname(__file__);bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
for o in bpy.data.objects:
 if o.type=='LIGHT':o.hide_render=True
world=bpy.data.worlds.new('RAWL_R2_Cutaway_World');s.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.55,.62,.72,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
sunD=bpy.data.lights.new('RAWL_R2_Cutaway_Sun','SUN');sunD.energy=2;sun=bpy.data.objects.new('RAWL_R2_Cutaway_Sun',sunD);s.collection.objects.link(sun);sun.rotation_euler=(math.radians(28),math.radians(-34),math.radians(-35))
camD=bpy.data.cameras.new('RAWL_R2_Cutaway_Camera');cam=bpy.data.objects.new('RAWL_R2_Cutaway_Camera',camD);s.collection.objects.link(cam);s.camera=cam
def render(name,eye,target,ortho=None,lens=40):
 cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
 if ortho:cam.data.type='ORTHO';cam.data.ortho_scale=ortho
 else:cam.data.type='PERSP';cam.data.lens=lens
 s.render.filepath=os.path.join(OUT,name+'.png');bpy.ops.render.render(write_still=True)
# Full source-plan cutaway, hide upper slabs/roof/exterior but retain all first-floor room boundaries/furniture.
for o in bpy.data.objects:
 if o.name.startswith(('RAWL_Roof','RAWL_Rooftop','RAWL_Masonry_Exterior_Walls','RAWL_East_Windows','RAWL_North_Windows','RAWL_South_Windows','RAWL_West_Windows','RAWL_SE_Diagonal_CurtainWall','RAWL_NW_Rotunda')) or o.name in ['RAWL_FloorSlab_L2','RAWL_FloorSlab_L3','RAWL_FloorSlab_L4','RAWL_FloorSlab_L5']:o.hide_render=True
for o in bpy.data.objects:
 if o.name.startswith('RAWL_2026_'):o.hide_render=True
render('first_floor_cutaway_round2',(8,14,82),(8,-2,0),ortho=108)
# Show documented multi-level atrium elements looking from the lower atrium up toward the glazed arched roof.
for o in bpy.data.objects:
 if o.name.startswith(('RAWL_Masonry_Exterior_Walls','RAWL_North_Windows','RAWL_South_Windows','RAWL_West_Windows','RAWL_East_Windows','RAWL_SE_Diagonal_CurtainWall','RAWL_NW_Rotunda')):o.hide_render=True
for o in bpy.data.objects:
 if o.name.startswith('RAWL_Roof_Main_Deck'):o.hide_render=True
# keep upper floor slabs and skylight so the historical atrium volume can be read
target=Vector((12,1,21));cam.location=(10,-1,2);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=26
s.render.filepath=os.path.join(OUT,'atrium_looking_up_round2.png');bpy.ops.render.render(write_still=True)
