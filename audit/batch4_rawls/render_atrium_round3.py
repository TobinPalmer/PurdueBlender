import bpy,os,math
from mathutils import Vector
OUT='audit/batch4_rawls';bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
keep={'RAWL_FloorSlab_L1_Ground','RAWL_Atrium_Mezzanine_Balustrades','RAWL_Atrium_Structural_Columns','RAWL_R2_Atrium_Railwork_EvidenceInformed'}
for o in bpy.data.objects:o.hide_render=o.name not in keep
# Preserve only ground plane and the source-informed columns and guardrails, expose full section
for o in bpy.data.objects:
 if o.type=='LIGHT':o.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('R3_Atrium_World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.52,.60,.70,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
ld=bpy.data.lights.new('R3_Atrium_Key','AREA');ld.energy=3000;ld.shape='DISK';ld.size=18;l=bpy.data.objects.new('R3_Atrium_Key',ld);s.collection.objects.link(l);l.location=(7,-10,25);l.rotation_euler=(math.radians(25),0,0)
camd=bpy.data.cameras.new('R3_Atrium_Camera');cam=bpy.data.objects.new('R3_Atrium_Camera',camd);s.collection.objects.link(cam);s.camera=cam;cam.location=(11,-40,17);cam.rotation_euler=(Vector((11,-1,11))-cam.location).to_track_quat('-Z','Y').to_euler();camd.lens=42
s.render.filepath=os.path.abspath(OUT+'/atrium_open_section_round3.png');bpy.ops.render.render(write_still=True)
