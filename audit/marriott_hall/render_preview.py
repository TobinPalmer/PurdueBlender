"""Create reproducible exterior and plan QA renders for Marriott Hall."""
import bpy
from pathlib import Path
from mathutils import Vector
here=Path(__file__).resolve().parent
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.studiolight_rotate_z=0.55
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH'
scene.display.shading.curvature_ridge_factor=1.2
scene.display.shading.curvature_valley_factor=1.0
scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
obj=bpy.data.objects['Marriot Hall']
world=[obj.matrix_world @ v.co for v in obj.data.vertices]
lo=Vector(tuple(min(v[i] for v in world) for i in range(3)))
hi=Vector(tuple(max(v[i] for v in world) for i in range(3)))
center=(lo+hi)*0.5
camdata=bpy.data.cameras.new('MRRT_QA_Camera'); cam=bpy.data.objects.new('MRRT_QA_Camera',camdata); scene.collection.objects.link(cam)
cam.location=center+Vector((-100,-110,80)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); camdata.type='ORTHO'; camdata.ortho_scale=max(hi.x-lo.x,hi.y-lo.y)*1.38; scene.camera=cam
scene.render.filepath=str(here/'preview_exterior.png'); bpy.ops.render.render(write_still=True)
cam.location=(center.x,center.y,max(hi.z+180,180)); cam.rotation_euler=(0,0,0); camdata.ortho_scale=max(hi.x-lo.x,hi.y-lo.y)*1.15
scene.render.filepath=str(here/'preview_plan.png'); bpy.ops.render.render(write_still=True)
print('MARRIOTT_PREVIEW_BOUNDS',list(lo),list(hi))
