import bpy
import os
from mathutils import Vector

folder=os.path.dirname(__file__)
obj=bpy.data.objects.get('Shreve Hall')
if obj is None: raise RuntimeError('Shreve object is missing')
scene=bpy.context.scene
for name in ('Shreve_Interior_Camera','Shreve_Interior_Area'):
    old=bpy.data.objects.get(name)
    if old: bpy.data.objects.remove(old,do_unlink=True)
camdata=bpy.data.cameras.new('Shreve_Interior_Camera')
camera=bpy.data.objects.new('Shreve_Interior_Camera',camdata); scene.collection.objects.link(camera)
camera.location=(-991.9,-100.2,1.62)
target=Vector((-997.2,-100.2,1.62))
camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
camdata.lens=28; scene.camera=camera
lightdata=bpy.data.lights.new('Shreve_Interior_Area','AREA')
light=bpy.data.objects.new('Shreve_Interior_Area',lightdata); scene.collection.objects.link(light)
light.location=(-993.2,-100.2,4.0)
light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
lightdata.energy=220; lightdata.shape='RECTANGLE'; lightdata.size=5.0; lightdata.size_y=3.0
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1200; scene.render.resolution_y=800; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(folder,'preview_interior.png')
scene.view_settings.view_transform='AgX'; scene.view_settings.exposure=-0.65
scene.world.color=(0.025,0.03,0.04)
bpy.ops.render.render(write_still=True)
print('RENDERED='+scene.render.filepath)
