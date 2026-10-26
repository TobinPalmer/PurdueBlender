import bpy, math
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'modular/buildings/bell_tower.blend'))
s=bpy.context.scene;c=bpy.data.collections['Asset_bell_tower']
# Render only the actual exported building; temporary review camera and light stay outside the asset collection.
for o in s.objects:
    if o.name not in c.objects and o.type not in {'LIGHT','CAMERA'}: o.hide_render=True
s.render.engine='BLENDER_EEVEE_NEXT';s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.render.image_settings.color_mode='RGBA';s.render.film_transparent=False
s.render.filepath=str(HERE/'overview.png')
camdata=bpy.data.cameras.new('Reviewer_Overview_Camera');cam=bpy.data.objects.new('Reviewer_Overview_Camera',camdata);s.collection.objects.link(cam);s.camera=cam;camdata.type='ORTHO';camdata.ortho_scale=58
cam.location=(34,-52,40);target=Vector((0,0,24));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(HERE/'overview.png');bpy.ops.render.render(write_still=True)
# Elevation style camera; captures full tower silhouette and entrance-like one facade.
cam.location=(0,-75,24);target=Vector((0,0,24));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camdata.ortho_scale=58
s.render.filepath=str(HERE/'front_elevation.png');bpy.ops.render.render(write_still=True)
print('rendered custom overview and front elevation')
