import bpy
import os
from mathutils import Vector

folder=os.path.dirname(__file__)
obj=bpy.data.objects.get('Shreve Hall')
if obj is None: raise RuntimeError('Shreve object is missing')
scene=bpy.context.scene
coords=[obj.matrix_world @ v.co for v in obj.data.vertices]
lo=Vector(tuple(min(p[i] for p in coords) for i in range(3)))
hi=Vector(tuple(max(p[i] for p in coords) for i in range(3)))
target=(lo+hi)*0.5
target.z=13.5
for name in ('Shreve_Overview_Camera','Shreve_Overview_Area'):
    old=bpy.data.objects.get(name)
    if old: bpy.data.objects.remove(old,do_unlink=True)
camdata=bpy.data.cameras.new('Shreve_Overview_Camera')
camera=bpy.data.objects.new('Shreve_Overview_Camera',camdata); scene.collection.objects.link(camera)
camera.location=target+Vector((-112.0,-112.0,78.0))
camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
camdata.type='ORTHO'; camdata.ortho_scale=126.0; scene.camera=camera
lightdata=bpy.data.lights.new('Shreve_Overview_Area','AREA')
light=bpy.data.objects.new('Shreve_Overview_Area',lightdata); scene.collection.objects.link(light)
light.location=target+Vector((-95.0,-65.0,118.0))
light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
lightdata.energy=2500; lightdata.shape='DISK'; lightdata.size=58.0
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1500; scene.render.resolution_y=1050; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(folder,'preview_overview.png')
scene.view_settings.view_transform='AgX'; scene.view_settings.exposure=-0.85
scene.world.color=(0.025,0.03,0.04)
bpy.ops.render.render(write_still=True)
print('RENDERED='+scene.render.filepath)
