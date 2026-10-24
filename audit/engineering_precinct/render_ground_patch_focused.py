import bpy
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
PATCH=ROOT/'modular'/'site'/'engineering_mall_groundwork_patch.blend'
OUT=ROOT/'audit'/'engineering_precinct'/'engineering_mall_ground_focused_review.png'
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
with bpy.data.libraries.load(str(PATCH),link=True) as (src,dst):
    dst.collections=['Engineering_Mall_Groundwork_Patch']
patch=dst.collections[0]; scene.collection.children.link(patch)
# Focus the material check on a representative section; foliage instances are hidden so ground
# coverage and surface detail can be evaluated without the expensive canopy assets.
for ob in patch.all_objects:
    if ob is not None and ob.type=='EMPTY' and ob.instance_type=='COLLECTION': ob.hide_render=True
cam_data=bpy.data.cameras.new('Focused_Ground_Check_Camera')
cam=bpy.data.objects.new('Focused_Ground_Check_Camera',cam_data); scene.collection.objects.link(cam)
cam.location=(38.0,153.0,36.0)
target=Vector((-12.0,112.0,0.0)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
cam_data.lens=42; cam_data.clip_end=1000; scene.camera=cam
world=bpy.data.worlds.new('Focused_Ground_Check_World'); world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.16,.19,.23,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8; scene.world=world
sun_data=bpy.data.lights.new('Focused_Ground_Check_Sun','SUN'); sun_data.energy=1.1; sun_data.angle=.12
sun=bpy.data.objects.new('Focused_Ground_Check_Sun',sun_data); scene.collection.objects.link(sun)
sun.rotation_euler=(.55,-.35,-.7)
scene.render.engine='BLENDER_EEVEE'; scene.eevee.taa_render_samples=8
scene.render.resolution_x=720; scene.render.resolution_y=520; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(OUT)
scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'
scene.view_settings.exposure=0
bpy.ops.render.render(write_still=True)
print('FOCUSED_GROUND_REVIEW',OUT)
