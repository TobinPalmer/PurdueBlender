import bpy
from mathutils import Vector
from pathlib import Path
root=Path(__file__).resolve().parent
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.studiolight_rotate_z=0.5
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH'
scene.display.shading.curvature_ridge_factor=1.25
scene.display.shading.curvature_valley_factor=1.0
obj=bpy.data.objects['Unitarian Universalist Church of Tippecanoe County']
pts=[obj.matrix_world @ v.co for v in obj.data.vertices]
lo=Vector(tuple(min(p[i] for p in pts) for i in range(3)))
hi=Vector(tuple(max(p[i] for p in pts) for i in range(3)))
center=(lo+hi)*0.5
center.z=4.5
cam_data=bpy.data.cameras.new('UUCTC_Preview_Camera')
cam=bpy.data.objects.new('UUCTC_Preview_Camera',cam_data)
scene.collection.objects.link(cam)
front_x=lo.x+0.2
cam.location=(front_x-57,center.y-43,center.z+42)
direction=center-cam.location
cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
cam_data.type='ORTHO'; cam_data.ortho_scale=77
scene.camera=cam
scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(root/'preview_exterior.png')
bpy.ops.render.render(write_still=True)
print('preview',scene.render.filepath,'bounds',list(lo),list(hi))

