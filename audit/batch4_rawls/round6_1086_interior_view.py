import bpy, os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'))
s=bpy.context.scene
# Render-only interior view inside the plan-derived 1086 footprint. The saved
# building is untouched; ceiling/glazing are hidden only to expose room depth.
for o in s.objects:
    o.hide_render=False
    if o.type=='LIGHT':o.hide_render=True
for n in ('RAWL_North_Windows_Glass','RAWL_Masonry_Exterior_Walls','RAWL_2026_PlanNWVestibule_03_00','RAWL_2026_PlanNWVestibule_01_01','RAWL_2026_Plan1086_04_00'):
    if n in bpy.data.objects:bpy.data.objects[n].hide_render=True
# Hide structural shells/slabs/roof from this room-focused interior camera only.
for o in bpy.data.objects:
    if any(k in o.name.lower() for k in ('roof','slab','ceiling','skylight')):o.hide_render=True
w=bpy.data.worlds.new('R6_1086_Interior_World');w.use_nodes=True
w.node_tree.nodes['Background'].inputs['Color'].default_value=(.68,.72,.76,1)
w.node_tree.nodes['Background'].inputs['Strength'].default_value=1.1;s.world=w
s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=900;s.render.image_settings.file_format='PNG'
cd=bpy.data.cameras.new('R6_1086_Interior_Camera');cam=bpy.data.objects.new('R6_1086_Interior_Camera',cd);s.collection.objects.link(cam)
cam.location=(27.5,7.5,1.6);cam.rotation_euler=(Vector((34,5.8,1.05))-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=32;s.camera=cam
for i,(loc,power,size) in enumerate([((31,7,5.5),1800,5),((35,3,5),1400,4),((29,3,4),1000,3)]):
    ld=bpy.data.lights.new('R6_1086_Interior_Fill_'+str(i),'AREA');ld.energy=power;ld.shape='DISK';ld.size=size
    lo=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(lo);lo.location=loc;lo.rotation_euler=(Vector((33,5,0))-lo.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=os.path.abspath('audit/batch4_rawls/north_1086_room_sightline_cutaway_round6.png')
bpy.ops.render.render(write_still=True)
print('Rendered room 1086 interior from within plan footprint; all render-only visibility/light changes unsaved.')
