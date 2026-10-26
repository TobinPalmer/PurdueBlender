import bpy, math
from mathutils import Vector
obj=bpy.data.objects.get("Martin C. Jischke Hall of Biomedical Engineering")
if obj is None: raise RuntimeError("MJIS asset object is missing")
pts=[obj.matrix_world @ v.co for v in obj.data.vertices]
mn=Vector((min(v.x for v in pts),min(v.y for v in pts),min(v.z for v in pts)))
mx=Vector((max(v.x for v in pts),max(v.y for v in pts),max(v.z for v in pts)))
c=(mn+mx)*0.5
scene=bpy.context.scene
cam_data=bpy.data.cameras.new("MJIS_Preview_Camera"); cam=bpy.data.objects.new("MJIS_Preview_Camera",cam_data); scene.collection.objects.link(cam)
cam.location=c+Vector((96,-112,78)); direction=c-cam.location; cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=max(mx.x-mn.x,mx.y-mn.y)*1.7; scene.camera=cam
ld=bpy.data.lights.new("MJIS_Preview_Sun","SUN"); lo=bpy.data.objects.new("MJIS_Preview_Sun",ld); scene.collection.objects.link(lo); lo.rotation_euler=(math.radians(26),math.radians(-22),math.radians(-34)); ld.energy=2.0
scene.render.engine='BLENDER_WORKBENCH'; scene.display.shading.light='STUDIO'; scene.display.shading.studio_light='paint.sl'; scene.display.shading.color_type='MATERIAL'; scene.display.shading.show_shadows=True; scene.display.shading.show_cavity=True
scene.render.resolution_x=960; scene.render.resolution_y=720; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=bpy.path.abspath('//../../audit/martin_c_jischke_hall/preview_detail.png')
scene.render.film_transparent=False
scene.view_settings.view_transform='Standard'; scene.view_settings.look='Medium High Contrast'
scene.world.color=(0.28,0.31,0.35)
bpy.ops.render.render(write_still=True)
for x in (cam,lo): bpy.data.objects.remove(x,do_unlink=True)
print("MJIS_PREVIEW="+scene.render.filepath)
