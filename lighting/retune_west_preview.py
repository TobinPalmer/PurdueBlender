import bpy
from mathutils import Vector
p=bpy.data.filepath;s=bpy.context.scene;cam=s.objects['SunsetCampusPreview_02'];cam.rotation_euler=(Vector((-7,17,190))-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam;s.render.filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\lighting\renders\sunset_cloud_preview_west.png';bpy.ops.wm.save_as_mainfile(filepath=p);bpy.ops.render.render(write_still=True)
