import bpy
from mathutils import Vector
from pathlib import Path
A=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_elliott')
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True;scene.display.shading.show_shadows=True
d=bpy.data.cameras.new('ELLT_R5_Exterior_Final_Camera');c=bpy.data.objects.new('ELLT_R5_Exterior_Final_Camera',d);scene.collection.objects.link(c)
c.location=(126,-135,82);d.type='ORTHO';d.ortho_scale=155;c.rotation_euler=(Vector((0,2,11))-c.location).to_track_quat('-Z','Y').to_euler();scene.camera=c
scene.render.filepath=str(A/'exterior_round5.png');bpy.ops.render.render(write_still=True)
