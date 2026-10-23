import bpy,pathlib
from mathutils import Vector
P=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');A=P/'audit/batch3_elliott';S=P/'modular/buildings/elliott_hall_of_music.blend'
bpy.ops.wm.open_mainfile(filepath=str(S));scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True;scene.display.shading.show_shadows=True
views=[('exterior_r4',(126,-135,82),(0,2,11),155),('bridge_detail_r4',(75,-10,32),(53,10.9,5.5),52)]
for name,loc,target,scale in views:
 d=bpy.data.cameras.new('TEMP_'+name);d.type='ORTHO';d.ortho_scale=scale;c=bpy.data.objects.new('TEMP_'+name,d);scene.collection.objects.link(c);c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();scene.camera=c;scene.render.filepath=str(A/(name+'.png'));bpy.ops.render.render(write_still=True)
print('Rendered saved and reopened Elliott views.')
