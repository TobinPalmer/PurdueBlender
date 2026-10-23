import bpy
from mathutils import Vector
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');bpy.ops.wm.open_mainfile(filepath=str(P/'modular/buildings/hovde_hall.blend'));s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=64;s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0.3;s.world.color=(.4,.4,.4)
root=bpy.data.objects['HOVD_Root'];entry=bpy.data.objects['HOVD_Portico_Entablature'].matrix_world.translation.copy();target=entry+Vector((0,0,-2.8));side=(root.matrix_world.to_3x3() @ Vector((1,0,0))).normalized();along=(root.matrix_world.to_3x3() @ Vector((0,1,0))).normalized()
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def light(n,loc,power,size):
 d=bpy.data.lights.new(n,'AREA');o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=loc;d.energy=power;d.shape='DISK';d.size=size;aim(o,target)
light('R3_Key',target+side*45+along*30+Vector((0,0,55)),1800,45);light('R3_Fill',target-side*35-along*5+Vector((0,0,28)),1200,50);light('R3_Rim',target+along*60+Vector((0,0,40)),900,45)
d=bpy.data.cameras.new('R3ExteriorCamera');o=bpy.data.objects.new('R3ExteriorCamera',d);s.collection.objects.link(o);o.location=target+side*75+along*26+Vector((0,0,22));aim(o,target);d.type='ORTHO';d.ortho_scale=100;s.camera=o
s.render.filepath=str(P/'audit/batch3_hovde/exterior_round3.png');bpy.ops.render.render(write_still=True);print('saved entrance-level facade render from reopened file')

