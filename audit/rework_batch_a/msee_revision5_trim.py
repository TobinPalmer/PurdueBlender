import bpy, os, math
from mathutils import Vector
ROOT=os.path.abspath('.'); asset=os.path.join(ROOT,'modular','buildings','materials_science_and_electrical_engineering_msee.blend')
OUT=os.path.join(ROOT,'audit','rework_batch_a')
bpy.ops.wm.open_mainfile(filepath=asset)
s=bpy.data.objects['MSEE_Max_W_Brown_two_story_glazed_atrium']; p=[s.matrix_world@v.co for v in s.data.vertices]; cen=sum(p,Vector())/len(p); t=Vector((.627,-.779,0)).normalized(); inward=Vector((-t.y,t.x,0))
for o in list(bpy.data.objects):
 if o.name.startswith(('R5_MSEE_entry_frame_vertical_','R5_MSEE_entry_transom','R5_MSEE_entry_arched_head','R5_MSEE_fanlight_spoke_')):
  o.location -= inward*.34
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=32; scene.render.resolution_x=1400; scene.render.resolution_y=900; scene.render.resolution_percentage=100; scene.render.filepath=os.path.join(OUT,'materials_science_and_electrical_engineering_msee_revision5_preview.png'); bpy.ops.render.render(write_still=True)
old=scene.camera; loc=cen-inward*42+Vector((0,0,8)); target=cen+Vector((0,0,3.9)); bpy.ops.object.camera_add(location=loc);cam=bpy.context.object;cam.name='TEMP_MSEE_R5_entry_camera';cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=60;scene.camera=cam;scene.render.resolution_x=1300;scene.render.resolution_y=900;scene.render.filepath=os.path.join(OUT,'materials_science_and_electrical_engineering_msee_revision5_entry_detail.png');bpy.ops.render.render(write_still=True);scene.camera=old;bpy.data.objects.remove(cam,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=asset); print('saved R5 trim, objects',len(bpy.data.collections['Asset_materials_science_and_electrical_engineering_msee'].all_objects))
