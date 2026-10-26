import bpy, math
from mathutils import Vector
s=bpy.context.scene
s.render.engine='BLENDER_EEVEE'; s.eevee.taa_render_samples=64
s.render.resolution_x=1400; s.render.resolution_y=1000; s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'; s.view_settings.view_transform='AgX'
w=s.world; w.use_nodes=True; bg=next(n for n in w.node_tree.nodes if n.type=='BACKGROUND'); bg.inputs['Color'].default_value=(0.27,0.31,0.39,1); bg.inputs['Strength'].default_value=.6
for o in bpy.data.objects: o.hide_render=True
def render_zone(prefixes,exclude=(),target=(0,0,0),camloc=(0,0,0),scale=32,file='out.png'):
    for o in bpy.data.objects:
        if o.type!='MESH': continue
        o.hide_render=o.name.startswith(prefixes) is False or o.name.startswith(exclude)
    cd=bpy.data.cameras.new('EvidenceCam_'+file); cd.type='ORTHO'; cd.ortho_scale=scale
    cam=bpy.data.objects.new('EvidenceCam_'+file,cd); s.collection.objects.link(cam)
    t=Vector(target); c=Vector(camloc); cam.location=c; cam.rotation_euler=(t-c).to_track_quat('-Z','Y').to_euler(); s.camera=cam
    s.render.filepath='//'+file; bpy.ops.render.render(write_still=True)
render_zone(('Tark_Lobby_',),target=(-3.5,-15,0.2),camloc=(-27,-37,45),scale=36,file='lobby_cutaway_r4.png')
render_zone(('Tark_PetesZa_','Tark_SharkTank_'),target=(-3.0,8.0,0.2),camloc=(-31,-28,53),scale=36,file='dining_recreation_cutaway_r4.png')
# Room 118 program: retain shell floor and one rear side wall for context, opening camera side.
for o in bpy.data.objects: o.hide_render=True
for o in bpy.data.objects:
    if o.type!='MESH' or not o.name.startswith('Tark_Dorm_'): continue
    if '_Wall_S' in o.name or '_Wall_E' in o.name or 'Door' in o.name: continue
    o.hide_render=False
cd=bpy.data.cameras.new('EvidenceCam_Room118'); cd.type='ORTHO'; cd.ortho_scale=9.8
cam=bpy.data.objects.new('EvidenceCam_Room118',cd); s.collection.objects.link(cam)
t=Vector((-37.4,-31.0,0.8)); c=Vector((-45,-43,23)); cam.location=c; cam.rotation_euler=(t-c).to_track_quat('-Z','Y').to_euler(); s.camera=cam
s.render.filepath='//representative_room118_r4.png'; bpy.ops.render.render(write_still=True)
