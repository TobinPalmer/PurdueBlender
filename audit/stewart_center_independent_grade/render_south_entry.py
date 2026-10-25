import bpy
from pathlib import Path
from mathutils import Vector

scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1600; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'
if scene.world is None: scene.world=bpy.data.worlds.new('Stewart_entry_review_world')
scene.world.use_nodes=True
scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.12,.15,.2,1)
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.28
target=Vector((-7,-48.5,6.4))
ld=bpy.data.lights.new('Stewart_entry_review_key','AREA'); ld.energy=2300; ld.shape='DISK'; ld.size=24
lo=bpy.data.objects.new('Stewart_entry_review_key',ld); scene.collection.objects.link(lo)
lo.location=target+Vector((5,-35,35)); lo.rotation_euler=(target-lo.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('Stewart_entry_review_camera'); cam=bpy.data.objects.new('Stewart_entry_review_camera',cd); scene.collection.objects.link(cam)
cam.location=target+Vector((12,-58,20)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); cd.lens=38
scene.camera=cam
out=Path(__file__).resolve().parent/'south_entry_r2.png'
scene.render.filepath=str(out); bpy.ops.render.render(write_still=True)
print(f'Rendered {out}')
