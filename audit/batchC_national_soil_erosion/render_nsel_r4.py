import bpy, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'batchC_national_soil_erosion'
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=32
scene.cycles.use_denoising=True
scene.render.resolution_x=1500
scene.render.resolution_y=1000
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'
scene.render.film_transparent=False

def aim(obj,target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def camera(name,loc,target,scale):
    data=bpy.data.cameras.new(name)
    obj=bpy.data.objects.new(name,data)
    scene.collection.objects.link(obj)
    obj.location=loc
    aim(obj,target)
    data.type='ORTHO'
    data.ortho_scale=scale
    return obj
def area(name,loc,target,energy,color,size):
    data=bpy.data.lights.new(name,'AREA')
    data.energy=energy
    data.color=color
    data.shape='DISK'
    data.size=size
    obj=bpy.data.objects.new(name,data)
    scene.collection.objects.link(obj)
    obj.location=loc
    aim(obj,target)
    return obj

world=scene.world
world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND')
old_strength=bg.inputs['Strength'].default_value
old_color=tuple(bg.inputs['Color'].default_value)
bg.inputs['Strength'].default_value=.28
bg.inputs['Color'].default_value=(.65,.70,.78,1)
old_camera=scene.camera
old_filepath=scene.render.filepath
temp=[]

# Exterior detail shot: a readable sign and entry with enough wall context to
# communicate scale. Warm key and cool fill create gentle raised-letter relief.
cam=camera('TEMP | NSEL R4 entrance perspective',(-4.5,-59,10.8),(-4,-25.0,4.0),21.0)
scene.camera=cam;temp.append(cam)
for args in (
    ('TEMP | NSEL R4 warm facade key',(-17,-45,17),(-4,-25,4.2),3800,(1.0,.76,.53),12),
    ('TEMP | NSEL R4 cool sign fill',(7,-43,10),(-4,-25,4.2),1900,(.68,.80,1.0),10),
    ('TEMP | NSEL R4 soft upper fill',(-1,-39,22),(-4,-25,4.2),1800,(1.0,.91,.78),13),
):
    light=area(*args);temp.append(light)
saved=[]
for obj in bpy.data.objects:
    saved.append((obj,obj.hide_render))
    if obj.name.startswith('TEMP |'):
        continue
    # Keep shell and facade details visible; hide room contents for this view.
    if obj.users_collection and any(c.name=='SOIL_Interior' for c in obj.users_collection):
        obj.hide_render=True
scene.render.filepath=str(AUDIT/'nsel_revision_r4_exterior_sign_lit.png')
bpy.ops.render.render(write_still=True)

# Interior cutaway: show the three retained room boundaries and ceiling lights,
# while opening the near west/south edges for inspection.
for obj,value in saved:
    obj.hide_render=value
for obj in bpy.data.objects:
    if obj.name.startswith('SOIL | R4 high-bay west liner wall') or obj.name.startswith('SOIL | R4 high-bay south end wall') or obj.name.startswith('SOIL | R4 high-bay ceiling'):
        obj.hide_render=True
    elif obj.name.startswith(('SOIL | R4','SOIL | R3','SOIL | R2 flume','SOIL | R2 overhead instrument','SOIL | R2 adjustable instrument','SOIL | R2 instrument gantry')):
        obj.hide_render=False
    elif obj.type=='LIGHT' and obj.name.startswith('SOIL Preview'):
        obj.hide_render=True
    else:
        obj.hide_render=True
cam.location=(-44,-27,17)
aim(cam,(-25.4,0,2.8))
cam.data.ortho_scale=43
scene.render.filepath=str(AUDIT/'nsel_revision_r4_enclosed_high_bay_cutaway.png')
bpy.ops.render.render(write_still=True)

# Restore scene state in memory. This file is only a render driver; it does not
# save camera, lighting, or visibility changes into the building asset.
for obj,value in saved:
    if obj.name in bpy.data.objects:
        obj.hide_render=value
scene.camera=old_camera
scene.render.filepath=old_filepath
bg.inputs['Strength'].default_value=old_strength
bg.inputs['Color'].default_value=old_color
for obj in temp:
    data=obj.data
    obj_type=obj.type
    bpy.data.objects.remove(obj,do_unlink=True)
    if data.users==0:
        (bpy.data.cameras if obj_type=='CAMERA' else bpy.data.lights).remove(data)
