import bpy, math
from mathutils import Vector
s=bpy.context.scene
s.render.engine='BLENDER_EEVEE'; s.eevee.taa_render_samples=64
s.render.resolution_x=1400; s.render.resolution_y=1000; s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'; s.render.film_transparent=False
s.view_settings.view_transform='AgX'
# Render an evidence-only cutaway: hide exterior shell; no source geometry is saved.
visible_prefixes=('Tark_Lobby_','Tark_PetesZa_','Tark_SharkTank_','Tark_North_Lounge_','Tark_North_Study_')
for o in bpy.data.objects:
    o.hide_render=not (o.type=='MESH' and o.name.startswith(visible_prefixes))
w=s.world; w.use_nodes=True
bg=next(n for n in w.node_tree.nodes if n.type=='BACKGROUND'); bg.inputs['Color'].default_value=(0.28,0.34,0.42,1); bg.inputs['Strength'].default_value=.65
ld=bpy.data.lights.new('TarkProgram_Key','AREA'); ld.energy=19000; ld.shape='DISK'; ld.size=38
light=bpy.data.objects.new('TarkProgram_Key',ld); s.collection.objects.link(light); light.location=(-20,-20,55); light.rotation_euler=(math.radians(22),0,math.radians(-20))
fd=bpy.data.lights.new('TarkProgram_Fill','AREA'); fd.energy=8500; fd.shape='DISK'; fd.size=30
fill=bpy.data.objects.new('TarkProgram_Fill',fd); s.collection.objects.link(fill); fill.location=(28,25,38); fill.rotation_euler=(math.radians(15),0,math.radians(150))
cd=bpy.data.cameras.new('TarkProgram_Camera'); cd.type='ORTHO'; cd.ortho_scale=68; cd.lens=50
cam=bpy.data.objects.new('TarkProgram_Camera',cd); s.collection.objects.link(cam); target=Vector((-3.0,8.0,0.0)); cam.location=(-54,-48,78); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler(); s.camera=cam
s.render.filepath='//central_program_r4.png'; bpy.ops.render.render(write_still=True)
# Representative room cutaway, with opaque walls hidden so furnishing detail reads clearly.
for o in bpy.data.objects: o.hide_render=True
for o in bpy.data.objects:
    if o.type!='MESH': continue
    n=o.name
    if n.startswith('Tark_Dorm_') or n.startswith('Tark_Representative_Room119_'):
        if '_Wall_' in n or 'Roof' in n or 'Door' in n: continue
        o.hide_render=False
# Include doors/walls along one edge for legibility only; open cutaway stays visible.
for n in ('Tark_Dorm_Room118_Wall_E','Tark_Dorm_Room118_Wall_N','Tark_Representative_Room119_Tark_Dorm_Room118_Wall_E'):
    if bpy.data.objects.get(n): bpy.data.objects[n].hide_render=False
# Ensure selected representative room neighborhood is framed (room 119 is offset by +6 m Y).
cd2=bpy.data.cameras.new('TarkRoomCutaway_Camera'); cd2.type='ORTHO'; cd2.ortho_scale=14
cam2=bpy.data.objects.new('TarkRoomCutaway_Camera',cd2); s.collection.objects.link(cam2)
target2=Vector((-37.2,-28.0,0.8)); cam2.location=(-49,-48,37); cam2.rotation_euler=(target2-Vector(cam2.location)).to_track_quat('-Z','Y').to_euler(); s.camera=cam2
# Warm practical and broad fill.
s.render.filepath='//representative_room_r4.png'; bpy.ops.render.render(write_still=True)
