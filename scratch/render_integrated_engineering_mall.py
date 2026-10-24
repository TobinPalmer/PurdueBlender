import bpy
from pathlib import Path
root=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
bpy.ops.wm.open_mainfile(filepath=str(root/'purdue_campus_master.blend'))
scene=bpy.context.scene
cam=bpy.data.objects.get('Cam_03_Engineering_Mall_WALC')
if cam is None: raise RuntimeError('Engineering Mall camera missing')
scene.camera=cam
scene.render.resolution_x=960; scene.render.resolution_y=540; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(root/'audit'/'engineering_precinct'/'integrated_master_engineering_mall.png')
# Use existing project render engine/settings to inspect the integrated result.
bpy.ops.render.render(write_still=True)
print('RENDERED',scene.render.filepath)
