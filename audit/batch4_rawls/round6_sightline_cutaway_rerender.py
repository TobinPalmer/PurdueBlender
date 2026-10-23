import bpy, os
from mathutils import Vector
blend=os.path.abspath('modular/buildings/rawls_hall.blend')
bpy.ops.wm.open_mainfile(filepath=blend)
s=bpy.context.scene
# Presentation-only cutaway. All geometry remains saved; the pane is omitted so
# the source-supported 1086 room behind it is actually legible in the image.
for o in s.objects:
    o.hide_render=False
    if o.type=='LIGHT': o.hide_render=True
for n in ('RAWL_North_Windows_Glass','RAWL_2026_PlanNWVestibule_03_00','RAWL_2026_PlanNWVestibule_01_01','RAWL_2026_Plan1086_04_00'):
    if n in bpy.data.objects: bpy.data.objects[n].hide_render=True
world=bpy.data.worlds.new('R6_Cutaway_World'); world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.6,.67,.73,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8; s.world=world
s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=900;s.render.image_settings.file_format='PNG'
camd=bpy.data.cameras.new('R6_1086_Cutaway_Camera'); cam=bpy.data.objects.new('R6_1086_Cutaway_Camera',camd);s.collection.objects.link(cam)
# Exterior eye through the actual north pane center toward a plan-derived desk.
pane=Vector((20.03,20.675,2.4)); desk=Vector((29.862,5.822,.795)); d=(desk-pane).normalized()
cam.location=pane-d*3.0; cam.rotation_euler=(desk-cam.location).to_track_quat('-Z','Y').to_euler();camd.lens=34;s.camera=cam
ld=bpy.data.lights.new('R6_Cutaway_Key','AREA');ld.energy=1800;ld.shape='DISK';ld.size=10
lo=bpy.data.objects.new('R6_Cutaway_Key',ld);s.collection.objects.link(lo);lo.location=(28,10,13);lo.rotation_euler=(Vector((30,6,1))-lo.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=os.path.abspath('audit/batch4_rawls/north_1086_room_sightline_cutaway_round6.png')
bpy.ops.render.render(write_still=True)
print('Rendered render-only pane-hidden cutaway; saved blend unchanged:',bpy.data.filepath)
