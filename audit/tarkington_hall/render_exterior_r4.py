import bpy, math
from mathutils import Vector
s=bpy.context.scene
s.render.engine='BLENDER_EEVEE'
s.eevee.taa_render_samples=32
s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
s.render.film_transparent=False
s.render.image_settings.file_format='PNG'
s.render.filepath='//../../audit/tarkington_hall/exterior_r4.png'
# isolate existing saved geometry from stale campus-coordinate lighting/cameras
for o in bpy.data.objects:
 if o.type in {'CAMERA','LIGHT'}: o.hide_render=True
# neutral sky and soft daylight
w=s.world
w.use_nodes=True
bg=next(n for n in w.node_tree.nodes if n.type=='BACKGROUND')
bg.inputs['Color'].default_value=(0.18,0.23,0.30,1)
bg.inputs['Strength'].default_value=0.45
sun_data=bpy.data.lights.new('TarkReview_Sun','SUN'); sun_data.energy=2.0
sun=bpy.data.objects.new('TarkReview_Sun',sun_data);s.collection.objects.link(sun);sun.rotation_euler=(math.radians(28),math.radians(-32),math.radians(-35))
area_data=bpy.data.lights.new('TarkReview_Key','AREA');area_data.energy=28000;area_data.shape='DISK';area_data.size=65
area=bpy.data.objects.new('TarkReview_Key',area_data);s.collection.objects.link(area);area.location=(15,-60,100);area.rotation_euler=(0,0,0)
# set area aimed downward
area.rotation_euler=(math.radians(15),0,math.radians(10))
# camera
cam_data=bpy.data.cameras.new('TarkReview_Camera');cam_data.type='ORTHO';cam_data.ortho_scale=180
cam=bpy.data.objects.new('TarkReview_Camera',cam_data);s.collection.objects.link(cam)
cam.location=(145,-170,123);target=Vector((0,0,8));cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler();s.camera=cam
bpy.ops.render.render(write_still=True)


