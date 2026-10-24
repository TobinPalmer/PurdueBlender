import bpy
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'batchC_national_soil_erosion'
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=40
scene.cycles.use_denoising=True
scene.render.resolution_x=1920
scene.render.resolution_y=1080
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'

def aim(obj,target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,target,energy,color,size):
    data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.color=color;data.shape='DISK';data.size=size
    obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.location=loc;aim(obj,target);return obj
def camera(name,loc,target,lens):
    data=bpy.data.cameras.new(name);data.type='PERSP';data.lens=lens
    obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.location=loc;aim(obj,target);return obj

world=scene.world;world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND')
old_bg_color=tuple(bg.inputs['Color'].default_value);old_bg_strength=bg.inputs['Strength'].default_value
old_camera=scene.camera;old_path=scene.render.filepath
bg.inputs['Color'].default_value=(.69,.72,.76,1);bg.inputs['Strength'].default_value=.36
temp=[]

# Street-distance front three-quarter view. The 30 mm lens at roughly 70 m
# from the face fits the overall elevation/roof profile while keeping the
# lettering at several hundred rendered pixels across.
cam=camera('TEMP | NSEL R5 street-distance front view',(-17,-99,13),(-2,-8,3.4),48)
scene.camera=cam;temp.append(cam)
for args in (
    ('TEMP | NSEL R5 warm street key',(-28,-58,25),(-2,-24,4),6200,(1.0,.78,.58),23),
    ('TEMP | NSEL R5 sky fill',(18,-56,15),(-2,-24,4),3600,(.68,.80,1.0),24),
    ('TEMP | NSEL R5 soft roof fill',(-2,-32,29),(-2,0,4),3800,(1.0,.91,.78),30),
):
    temp.append(area(*args))

saved=[]
for obj in bpy.data.objects:
    saved.append((obj,obj.hide_render))
    if any(c.name=='SOIL_Interior' for c in obj.users_collection):
        obj.hide_render=True
scene.render.filepath=str(AUDIT/'nsel_revision_r5_street_distance.png')
bpy.ops.render.render(write_still=True)

# High-bay cutaway retains warm wall-panel variation and equipment colors.
for obj,value in saved: obj.hide_render=value
for obj in temp:
    if obj.type=='LIGHT': obj.hide_render=True
for obj in bpy.data.objects:
    if obj.name.startswith(('SOIL | R4 high-bay west liner wall','SOIL | R4 high-bay south end wall','SOIL | R4 high-bay ceiling','SOIL | R4 west wall liner joint','SOIL | R4 wall base guard -1','SOIL | R5 west lower wall band','SOIL | R5 west cladding panel','SOIL | R5 wall girt -1')):
        obj.hide_render=True
    elif obj.name.startswith(('SOIL | R2 flume','SOIL | R2 overhead instrument','SOIL | R2 adjustable instrument','SOIL | R2 instrument gantry','SOIL | R3','SOIL | R4','SOIL | R5')):
        obj.hide_render=False
    elif obj.type=='LIGHT' and obj.name.startswith('SOIL Preview'):
        obj.hide_render=True
    else:
        obj.hide_render=True
for args in (
    ('TEMP | NSEL R5 interior warm key',(-30,-15,12),(-25.4,0,2.6),2400,(1.0,.79,.57),16),
    ('TEMP | NSEL R5 interior neutral fill',(-21,-2,10),(-25.4,0,2.6),1900,(.77,.86,1.0),14),
    ('TEMP | NSEL R5 interior rear fill',(-28,13,11),(-25.4,0,2.6),1400,(1.0,.91,.73),12),
):
    temp.append(area(*args))
cam.location=(-43,-27,17);aim(cam,(-25.4,0,2.8));cam.data.lens=50;cam.data.type='ORTHO';cam.data.ortho_scale=43
scene.render.filepath=str(AUDIT/'nsel_revision_r5_high_bay_context.png')
bpy.ops.render.render(write_still=True)

for obj,value in saved:
    if obj.name in bpy.data.objects: obj.hide_render=value
scene.camera=old_camera;scene.render.filepath=old_path
bg.inputs['Color'].default_value=old_bg_color;bg.inputs['Strength'].default_value=old_bg_strength
for obj in temp:
    data=obj.data;typ=obj.type
    bpy.data.objects.remove(obj,do_unlink=True)
    if data.users==0:
        (bpy.data.cameras if typ=='CAMERA' else bpy.data.lights).remove(data)
