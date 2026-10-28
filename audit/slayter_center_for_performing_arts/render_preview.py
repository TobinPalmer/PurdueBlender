"""Render a readable front three-quarter view of the Slayter venue asset."""
import bpy, json, os, math
from mathutils import Vector
here=os.path.dirname(os.path.abspath(__file__))
cfg=json.load(open(os.path.join(here,'build_config.json'),encoding='utf-8'))
obj=bpy.data.objects.get(cfg['object_name'])
if obj is None: raise RuntimeError('Slayter object missing')
world=[obj.matrix_world@Vector(p) for p in obj.bound_box]
# Frame the pavilion, with just enough audience knoll to read its open-air setting.
lo=Vector((min(v.x for v in world),min(v.y for v in world),min(v.z for v in world)))
hi=Vector((max(v.x for v in world),max(v.y for v in world),max(v.z for v in world)))
center=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,(lo.z+hi.z)/2))
center.x-=3.5
size=max(hi-lo)
cd=bpy.data.cameras.new('SlayterReviewCamera')
cam=bpy.data.objects.new('SlayterReviewCamera',cd); bpy.context.scene.collection.objects.link(cam)
cam.location=center+Vector((size*1.9,-size*.10,size*.32))
cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
cd.type='ORTHO'; cd.ortho_scale=size*1.08; bpy.context.scene.camera=cam
for name,offset,power,area in [
    ('SlayterKey',(0,-size*.9,size*1.5),size*size*2.5,size*.9),
    ('SlayterFill',(-size*.2,size*.7,size*.8),size*size*1.1,size*1.1),
    ('SlayterRim',(size*.4,size*.5,size*1.2),size*size*1.6,size*.7)]:
    ld=bpy.data.lights.new(name,'AREA'); ld.energy=power; ld.shape='DISK'; ld.size=area
    light=bpy.data.objects.new(name,ld); bpy.context.scene.collection.objects.link(light)
    light.location=center+Vector(offset); light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene
try: scene.render.engine='BLENDER_EEVEE_NEXT'
except TypeError: scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1440; scene.render.resolution_y=960; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(here,'preview_detail.png')
scene.render.image_settings.color_mode='RGBA'; scene.render.film_transparent=False
scene.render.resolution_percentage=100
if scene.world is None: scene.world=bpy.data.worlds.new('SlayterReviewWorld')
scene.world.use_nodes=True
background=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND')
background.inputs['Color'].default_value=(.27,.31,.36,1); background.inputs['Strength'].default_value=.45
scene.view_settings.view_transform='AgX'
scene.camera.data.lens=48
scene.render.image_settings.color_depth='8'
bpy.ops.render.render(write_still=True)
print('SLAYTER_PREVIEW='+scene.render.filepath)
