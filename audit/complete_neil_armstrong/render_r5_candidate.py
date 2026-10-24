import bpy, math, os, json
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
scene=bpy.context.scene
# temporary non-saved review camera and light rig
camdata=bpy.data.cameras.new('R5_Review_Camera_Data'); cam=bpy.data.objects.new('R5_Review_Camera',camdata); scene.collection.objects.link(cam)
cam.location=(145,-155,108); target=Vector((0,-9,9)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler(); camdata.lens=55; camdata.clip_end=1000; scene.camera=cam
lightdata=bpy.data.lights.new('R5_Review_Key_Data','AREA'); light=bpy.data.objects.new('R5_Review_Key',lightdata); scene.collection.objects.link(light); light.location=(-70,-90,120); lightdata.energy=5200; lightdata.shape='DISK'; lightdata.size=100; light.rotation_euler=(Vector((0,-10,8))-Vector(light.location)).to_track_quat('-Z','Y').to_euler()
filldata=bpy.data.lights.new('R5_Review_Fill_Data','AREA'); fill=bpy.data.objects.new('R5_Review_Fill',filldata); scene.collection.objects.link(fill); fill.location=(50,60,85); filldata.energy=2600; filldata.shape='DISK'; filldata.size=90; fill.rotation_euler=(Vector((0,-10,8))-Vector(fill.location)).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.render.resolution_x=1600; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\complete_neil_armstrong\renders_r5\exterior_lidar_wings_r5.png'
scene.render.film_transparent=False
scene.world.color=(0.32,0.38,0.48)
os.makedirs(os.path.dirname(scene.render.filepath),exist_ok=True)
bpy.ops.render.render(write_still=True)
print('rendered',scene.render.filepath)
