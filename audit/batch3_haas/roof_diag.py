import bpy
from mathutils import Vector
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.render.resolution_x=800;s.render.resolution_y=600;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.exposure=-1.2
camd=bpy.data.cameras.new('Roof diagnosis');cam=bpy.data.objects.new('Roof diagnosis',camd);s.collection.objects.link(cam);s.camera=cam;camd.type='ORTHO';camd.ortho_scale=82;cam.location=(80,-12,38);cam.rotation_euler=(Vector((-6,0,6))-cam.location).to_track_quat('-Z','Y').to_euler()
for name in ['HAAS_Photo_Main_Hipped_Roof','HAAS_Photo_Entrance_Hipped_Roof']:bpy.data.objects[name].hide_render=True
s.render.filepath='C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas/roof_hidden_diag.png';bpy.ops.render.render(write_still=True)
