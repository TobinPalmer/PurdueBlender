import bpy
from mathutils import Vector
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1600; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world.color=(0.15,0.15,0.15)
# moderate studio lighting
ld=bpy.data.lights.new('Review_Key','AREA'); lo=bpy.data.objects.new('Review_Key',ld); scene.collection.objects.link(lo); lo.location=(-455,370,45); ld.energy=3500; ld.shape='DISK'; ld.size=28
ld2=bpy.data.lights.new('Review_Fill','AREA'); lo2=bpy.data.objects.new('Review_Fill',ld2); scene.collection.objects.link(lo2); lo2.location=(-405,450,30); ld2.energy=1200; ld2.size=25
camd=bpy.data.cameras.new('Review_Camera'); cam=bpy.data.objects.new('Review_Camera',camd); scene.collection.objects.link(cam); cam.location=(-430,365,25); target=Vector((-430,410,8)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler(); camd.type='ORTHO'; camd.ortho_scale=43; scene.camera=cam
scene.render.filepath=r'audit/phi_gamma_delta/initial_south_oblique.png'
bpy.ops.render.render(write_still=True)
