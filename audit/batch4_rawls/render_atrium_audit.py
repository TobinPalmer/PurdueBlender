import bpy,math,os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend');s=bpy.context.scene
# hide exterior and roof to expose existing atrium structure for audit render
for o in bpy.data.objects:
 if o.name.startswith(('RAWL_Masonry_Exterior','RAWL_East_Windows','RAWL_North_Windows','RAWL_South_Windows','RAWL_West_Windows','RAWL_SE_Diagonal_CurtainWall','RAWL_NW_Rotunda','RAWL_Limestone','RAWL_Roof')):o.hide_render=True
for o in bpy.data.objects:
 if o.type=='LIGHT':o.hide_render=True
world=bpy.data.worlds.get('RAWL_Batch4_World') or bpy.data.worlds.new('RAWL_Batch4_World');s.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.55,.62,.72,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
ld=bpy.data.lights.new('R2_Atrium_Sun','SUN');ld.energy=2.0;sun=bpy.data.objects.new('R2_Atrium_Sun',ld);s.collection.objects.link(sun);sun.rotation_euler=(math.radians(20),math.radians(-30),math.radians(-20))
ld2=bpy.data.lights.new('R2_Atrium_Fill','AREA');ld2.energy=2500;ld2.shape='DISK';ld2.size=16;l2=bpy.data.objects.new('R2_Atrium_Fill',ld2);s.collection.objects.link(l2);l2.location=(10,-18,15);l2.rotation_euler=(math.radians(70),0,0)
camd=bpy.data.cameras.new('R2_Atrium_Camera');cam=bpy.data.objects.new('R2_Atrium_Camera',camd);s.collection.objects.link(cam);s.camera=cam
cam.location=(11,-34,13);target=Vector((11,-1,13));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camd.lens=45
s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=os.path.abspath('audit/batch4_rawls/atrium_exposed_round2.png')
bpy.ops.render.render(write_still=True)
