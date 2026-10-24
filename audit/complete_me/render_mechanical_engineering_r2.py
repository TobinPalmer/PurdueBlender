"""Render the evidence-changed FID108 roof mass from the reopened R2 asset."""
import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'complete_me'
scene=bpy.context.scene
camdata=bpy.data.cameras.new('ME_R2_Cam_FID108_Aerial_Data')
cam=bpy.data.objects.new('ME_R2_Cam_FID108_Aerial',camdata)
scene.collection.objects.link(cam)
cam.location=(50,-24,46)
cam.rotation_euler=(Vector((41.4,-17.6,1.0))-cam.location).to_track_quat('-Z','Y').to_euler()
camdata.type='ORTHO';camdata.ortho_scale=58
scene.camera=cam
scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(AUDIT/'mechanical_engineering_r2_fid108_aerial.png')
bpy.ops.render.render(write_still=True)
print('R2 aerial render:',scene.render.filepath)
