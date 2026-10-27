import bpy, os, math
from pathlib import Path
from mathutils import Vector
audit=Path(__file__).resolve().parent
obj=bpy.data.objects.get('House_301840871')
coll=bpy.data.collections.get('Asset_massing_house_301840871_5d1bc06')
if obj is None or coll is None or len(coll.objects)!=1: raise RuntimeError('Kappa Kappa Gamma model missing')
pts=[obj.matrix_world@v.co for v in obj.data.vertices]
lo=Vector(tuple(min(p[i] for p in pts) for i in range(3))); hi=Vector(tuple(max(p[i] for p in pts) for i in range(3))); center=(lo+hi)*0.5
span=max(hi.x-lo.x,hi.y-lo.y,hi.z-lo.z)
scene=bpy.context.scene
cam_data=bpy.data.cameras.new('KKG_Preview_Camera'); cam=bpy.data.objects.new('KKG_Preview_Camera',cam_data); scene.collection.objects.link(cam)
cam.location=center+Vector((-span*1.42,span*0.55,span*0.12)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); cam_data.type='ORTHO'; cam_data.ortho_scale=span*1.52; scene.camera=cam
light_data=bpy.data.lights.new('KKG_Preview_Area','AREA'); light=bpy.data.objects.new('KKG_Preview_Area',light_data); scene.collection.objects.link(light); light.location=center+Vector((-span, -span*0.9,span*1.5)); light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler(); light_data.energy=span*span*0.020; light_data.shape='DISK'; light_data.size=span*0.9
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(audit/'preview.png'); scene.world.color=(0.03,0.03,0.03); scene.world.use_nodes=True; bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(0.12,0.12,0.12,1); bg.inputs['Strength'].default_value=0.45; scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=-0.10
bpy.ops.render.render(write_still=True); print('RENDERED='+scene.render.filepath)
