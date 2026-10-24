import bpy, os
from mathutils import Vector
ROOT=os.path.abspath('.'); p=os.path.join(ROOT,'modular','buildings','materials_science_and_electrical_engineering_msee.blend')
bpy.ops.wm.open_mainfile(filepath=p)
screen=bpy.data.objects['MSEE_Max_W_Brown_two_story_glazed_atrium']; pts=[screen.matrix_world@v.co for v in screen.data.vertices]
center=sum(pts,Vector())/len(pts); tangent=Vector((.627,-.779,0)).normalized(); outward=Vector((-tangent.y,tangent.x,0))
target=center+Vector((0,0,3.7)); loc=center-outward*42+Vector((0,0,8))
bpy.ops.object.camera_add(location=loc); cam=bpy.context.object; cam.name='TEMP_MSEE_entry_close'; cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=60
s=bpy.context.scene; old=s.camera; s.camera=cam; s.render.engine='CYCLES'; s.cycles.samples=32; s.render.resolution_x=1300; s.render.resolution_y=900; s.render.resolution_percentage=100; s.render.filepath=os.path.join(ROOT,'audit','rework_batch_a','materials_science_and_electrical_engineering_msee_revision5_entry_detail.png')
bpy.ops.render.render(write_still=True)

