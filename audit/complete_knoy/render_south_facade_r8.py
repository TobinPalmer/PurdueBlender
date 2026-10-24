import bpy, math
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
s=bpy.context.scene
camd=bpy.data.cameras.new('KNOY_R8_Source_Facade_Check_Camera');cam=bpy.data.objects.new('KNOY_R8_Source_Facade_Check_Camera',camd);s.collection.objects.link(cam)
cam.location=(0,-78,9);target=Vector((0,0,9));cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=58;s.camera=cam
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1600;s.render.resolution_y=1050;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\complete_knoy\knoy_south_facade_source_review_r8.png'
bpy.ops.render.render(write_still=True)
print('Saved temporary front facade evidence render without saving blend.')

