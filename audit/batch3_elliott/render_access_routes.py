import bpy,pathlib
from mathutils import Vector
P=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');A=P/'audit/batch3_elliott';SRC=P/'modular/buildings/elliott_hall_of_music.blend';bpy.ops.wm.open_mainfile(filepath=str(SRC));
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True;scene.display.shading.show_shadows=True
for ob in bpy.data.objects:
 if ob.name.startswith('ELLT_Access_') and ('Estimated_Level_Interior_Route' in ob.name or 'Estimated_Wheelchair_Clear_Space' in ob.name): ob.hide_render=False
 elif ob.name.startswith('ELLT_Access_'): ob.hide_render=True
 if ob.name.startswith('ELLT_Exterior_') or ob.name.startswith('ELLT_Estimated_') or 'Footprint_Exterior_Walls' in ob.name or 'Footprint_Roof' in ob.name: ob.hide_render=True
 if ob.name=='ELLT_B3_ceiling': ob.hide_render=True
camd=bpy.data.cameras.new('ELLT_Round3_Access_Top_Cam');camd.type='ORTHO';camd.ortho_scale=96;cam=bpy.data.objects.new('ELLT_Round3_Access_Top_Cam',camd);scene.collection.objects.link(cam);cam.location=(0,0,95);cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam;scene.render.filepath=str(A/'round3_access_routes_top.png');bpy.ops.render.render(write_still=True)
