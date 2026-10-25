import bpy
from pathlib import Path
from mathutils import Vector

scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1600; scene.render.resolution_y=1100
scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'
if scene.world is None: scene.world=bpy.data.worlds.new('Stewart_r3_review_world')
scene.world.use_nodes=True
scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.12,.15,.2,1)
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.28
target=Vector((-7.65,-48.0,6.0))
ld=bpy.data.lights.new('Stewart_r3_review_key','AREA'); ld.energy=2500; ld.shape='DISK'; ld.size=24
lo=bpy.data.objects.new('Stewart_r3_review_key',ld); scene.collection.objects.link(lo)
lo.location=target+Vector((0,-45,32)); lo.rotation_euler=(target-lo.location).to_track_quat('-Z','Y').to_euler()
out=Path(__file__).resolve().parent
views=[('south_entry_r3',Vector((4,-68,18)),42),('south_oblique_r3',Vector((42,-118,82)),48)]
for name,offset,lens in views:
    cd=bpy.data.cameras.new(f'Stewart_r3_{name}'); cam=bpy.data.objects.new(f'Stewart_r3_{name}',cd); scene.collection.objects.link(cam)
    cam.location=target+offset; cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); cd.lens=lens
    scene.camera=cam; scene.render.filepath=str(out/f'{name}.png'); bpy.ops.render.render(write_still=True)
    print(f'Rendered {scene.render.filepath}')
