import bpy
from mathutils import Vector
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');bpy.ops.wm.open_mainfile(filepath=str(P/'modular/buildings/hovde_hall.blend'));s=bpy.context.scene;c=bpy.data.collections['Asset_hovde_hall']
for o in c.all_objects:
 if o:o.hide_render=True
obj=bpy.data.objects['HOVD_Pres_Desk_Top'];obj.hide_render=False;center=obj.matrix_world.translation.copy();obj.scale=(1,1,1)
floor=bpy.data.objects['HOVD_Pres_Floor'];floor.hide_render=True
d=bpy.data.cameras.new('debug');cam=bpy.data.objects.new('debug',d);s.collection.objects.link(cam);cam.location=center+Vector((0,0,10));cam.rotation_euler=(Vector(center)-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=6;s.camera=cam
ld=bpy.data.lights.new('debug','AREA');lo=bpy.data.objects.new('debug',ld);s.collection.objects.link(lo);lo.location=center+Vector((0,0,8));ld.energy=2000;ld.size=8;lo.rotation_euler=(Vector(center)-lo.location).to_track_quat('-Z','Y').to_euler()
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=800;s.render.resolution_y=800;s.view_settings.exposure=1;s.render.filepath=str(P/'audit/batch3_hovde/debug_pres_desk_only.png');bpy.ops.render.render(write_still=True)
