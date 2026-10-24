import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]; PATCH=ROOT/'modular/site/engineering_mall_groundwork_patch.blend'; OUT=ROOT/'audit/engineering_precinct/engineering_mall_plaza_overhead_before.png'
bpy.ops.wm.read_factory_settings(use_empty=True); scene=bpy.context.scene
with bpy.data.libraries.load(str(PATCH),link=True) as (src,dst): dst.collections=['Engineering_Mall_Groundwork_Patch']
scene.collection.children.link(dst.collections[0]); col=dst.collections[0]
for ob in col.all_objects:
 if ob is not None and ob.type=='EMPTY' and ob.instance_type=='COLLECTION': ob.hide_render=True
camd=bpy.data.cameras.new('Plaza_Overhead_Camera'); camd.type='ORTHO'; camd.ortho_scale=62
cam=bpy.data.objects.new('Plaza_Overhead_Camera',camd); scene.collection.objects.link(cam); cam.location=(-7,137,100); cam.rotation_euler=(0,0,0); cam.rotation_euler=(Vector((-7,137,0))-cam.location).to_track_quat('-Z','Y').to_euler(); scene.camera=cam
scene.render.engine='BLENDER_EEVEE'; scene.eevee.taa_render_samples=8; scene.render.resolution_x=900; scene.render.resolution_y=900; scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(OUT); scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'
world=bpy.data.worlds.new('OverheadWorld'); world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.2,.23,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8; scene.world=world
sun_d=bpy.data.lights.new('Sun','SUN'); sun_d.energy=2; sun=bpy.data.objects.new('Sun',sun_d); scene.collection.objects.link(sun); sun.rotation_euler=(.45,-.3,-.8)
bpy.ops.render.render(write_still=True); print('SAVED',OUT)
