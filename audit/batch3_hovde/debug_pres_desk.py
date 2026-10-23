import bpy
from mathutils import Vector
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');bpy.ops.wm.open_mainfile(filepath=str(P/'modular/buildings/hovde_hall.blend'));s=bpy.context.scene;c=bpy.data.collections['Asset_hovde_hall']
for o in c.all_objects:
 if o:o.hide_render=True
for n in ['HOVD_Pres_Floor','HOVD_Pres_Desk_Top','HOVD_Pres_Desk_Ped_L','HOVD_Pres_Desk_Ped_R']:
 bpy.data.objects[n].hide_render=False
floor=bpy.data.objects['HOVD_Pres_Floor'];center=floor.matrix_world.translation.copy();d=bpy.data.cameras.new('debug');cam=bpy.data.objects.new('debug',d);s.collection.objects.link(cam);cam.location=center+Vector((0,0,20));cam.rotation_euler=(Vector(center)-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=15;s.camera=cam
ld=bpy.data.lights.new('debug','AREA');lo=bpy.data.objects.new('debug',ld);s.collection.objects.link(lo);lo.location=center+Vector((0,0,15));ld.energy=3000;ld.size=15;lo.rotation_euler=(Vector(center)-lo.location).to_track_quat('-Z','Y').to_euler()
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1000;s.render.resolution_y=800;s.view_settings.exposure=1;s.render.filepath=str(P/'audit/batch3_hovde/debug_pres_desk.png');bpy.ops.render.render(write_still=True);print('desk world',tuple(bpy.data.objects['HOVD_Pres_Desk_Top'].matrix_world.translation),'center',tuple(center))
