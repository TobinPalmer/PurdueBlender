import bpy
from mathutils import Vector
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');bpy.ops.wm.open_mainfile(filepath=str(P/'modular/buildings/hovde_hall.blend'))
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
sh=s.display.shading;sh.light='STUDIO';sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.cavity_ridge_factor=1.2;sh.cavity_valley_factor=1.0;sh.show_specular_highlight=True;sh.background_type='WORLD';sh.background_color=(.12,.15,.19)
col=bpy.data.collections['Asset_hovde_hall']
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def camera(loc,target,scale):
 d=bpy.data.cameras.new('Hovde Review Camera');o=bpy.data.objects.new('Hovde Review Camera',d);s.collection.objects.link(o);o.location=loc;aim(o,target);d.type='ORTHO';d.ortho_scale=scale;s.camera=o
camera((105,15,34),(-9,15,8),105)
s.render.filepath=str(P/'audit/batch3_hovde/exterior_material_preview.png');bpy.ops.render.render(write_still=True)
# Isolated representative president's office, with ceiling removed for a clean cutaway.
for o in list(col.all_objects):
 if o is not None:o.hide_render=not (o.name.startswith('HOVD_Pres_') and not o.name.endswith('_Ceiling'))
s.render.resolution_x=1100;s.render.resolution_y=1000;camera((2.5,-4.5,65),(2.5,-4.5,5),22)
s.render.filepath=str(P/'audit/batch3_hovde/presidential_office_cutaway.png');bpy.ops.render.render(write_still=True)
# Board of Trustees room as a separate cutaway, including table and both chair rows.
for o in list(col.all_objects):
 if o is not None:o.hide_render=not (o.name.startswith(('HOVD_Board_','HOVD_Chair_','HOVD_Mic_','HOVD_Portfolio_')) and not o.name.endswith('_Ceiling'))
s.render.resolution_x=1100;s.render.resolution_y=1000;camera((-29,34,65),(-29,34,5),34)
s.render.filepath=str(P/'audit/batch3_hovde/trustees_boardroom_cutaway.png');bpy.ops.render.render(write_still=True)
print('Rendered Workbench material previews; all three came from reopened saved source asset')
