import bpy
from pathlib import Path
HERE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(HERE.parents[1]/'modular/buildings/bell_tower.blend'))
s=bpy.context.scene
s.render.engine='BLENDER_EEVEE_NEXT'
s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.filepath=str(HERE/'scene_camera_preview.png')
bpy.ops.render.render(write_still=True)
print('rendered',s.render.filepath,'camera',s.camera.name if s.camera else None)
