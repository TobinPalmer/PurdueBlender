import bpy, math
from mathutils import Vector
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'modular/buildings/knoy_hall.blend'))
scene=bpy.context.scene
cam_data=bpy.data.cameras.new('KNOY_R11_Entrance_Review_Camera')
cam=bpy.data.objects.new('KNOY_R11_Entrance_Review_Camera',cam_data)
scene.collection.objects.link(cam)
cam.location=(0.756,-52.3,4.15)
target=Vector((0.756,-46.32,4.0))
cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
cam_data.lens=45
scene.camera=cam
# Soft, legible evidence lighting; only for this inspection render.
light_data=bpy.data.lights.new('KNOY_R11_Entrance_Key','AREA')
light=bpy.data.objects.new('KNOY_R11_Entrance_Key',light_data)
scene.collection.objects.link(light)
light.location=(-2,-50,8)
light_data.energy=900
light_data.shape='DISK';light_data.size=5
light.rotation_euler=(Vector((0.756,-46.2,3.8))-Vector(light.location)).to_track_quat('-Z','Y').to_euler()
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH'
scene.display.shading.curvature_ridge_factor=1.2
scene.display.shading.curvature_valley_factor=1.0
scene.render.resolution_x=1200;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(ROOT/'audit/complete_knoy/knoy_entrance_detail_r11.png')
scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
bpy.ops.render.render(write_still=True)
print('Rendered entrance close-up')
