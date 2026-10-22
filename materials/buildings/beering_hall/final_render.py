import bpy,os
from mathutils import Vector
s=bpy.context.scene;c=bpy.data.collections['Asset_beering_hall']
for o in c.all_objects:
 if o.name.startswith('BRNG_PBR_Tower_Window_'):o.location.z-=.5
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
s.render.filepath=os.path.abspath('materials/buildings/beering_hall/hero.png');bpy.ops.render.render(write_still=True)
cam=s.camera;cam.location=(-50,-42,9);cam.rotation_euler=(Vector((-36,-22,7))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=54;s.render.filepath=os.path.abspath('materials/buildings/beering_hall/closeup.png');bpy.ops.render.render(write_still=True)
