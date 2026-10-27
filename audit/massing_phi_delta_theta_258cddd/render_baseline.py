import bpy, math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/massing_phi_delta_theta_258cddd.blend')
sc=bpy.context.scene
obj=bpy.data.objects.get('Phi Delta Theta')
sc.render.engine='BLENDER_EEVEE'
sc.render.resolution_x=1400; sc.render.resolution_y=1000; sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
sc.render.film_transparent=False
sc.world.color=(0.18,0.18,0.18)
# camera aimed at center, south view looking north and modest elevated
cdata=bpy.data.cameras.new('AuditCamera'); cam=bpy.data.objects.new('AuditCamera',cdata); sc.collection.objects.link(cam); sc.camera=cam
center=Vector((89,-405,7.8)); cam.location=center+Vector((7,-74,20)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); cdata.type='ORTHO'; cdata.ortho_scale=62
ld=bpy.data.lights.new('Key','AREA'); lo=bpy.data.objects.new('Key',ld); sc.collection.objects.link(lo); lo.location=(50,-445,55); ld.energy=5000; ld.size=35
sc.render.filepath=r'audit/massing_phi_delta_theta_258cddd/renders/baseline_south.png'
bpy.ops.render.render(write_still=True)
