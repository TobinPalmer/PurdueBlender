import bpy,math
from mathutils import Vector
for o in bpy.data.objects:
 if o.type=='MESH' and not ('TracePartition' in o.name or 'L1_Ground' in o.name):o.hide_render=True
bpy.ops.object.camera_add(location=(0,0,150));cam=bpy.context.object;cam.rotation_euler=(0,0,0);cam.rotation_euler=(0,0,0);cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=105
s=bpy.context.scene;s.camera=cam;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.render.resolution_x=700;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.filepath='//../../audit/complete_knoy/reviewer_cutaway.png';bpy.ops.render.render(write_still=True)
