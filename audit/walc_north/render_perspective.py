exec(open(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/walc_north/render_after.py').read().split('bpy.ops.object.camera_add')[0])
from mathutils import Vector
bpy.ops.object.camera_add(location=(110,-150,180));cam=bpy.context.object;cam.rotation_euler=(Vector((-85,55,6))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=215;scene.camera=cam;scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100
for o in bpy.context.scene.objects:
 if o.type=='CURVE':o.hide_render=True
scene.render.filepath=str(P/'audit/walc_north/affected_after.png');bpy.ops.render.render(write_still=True)
