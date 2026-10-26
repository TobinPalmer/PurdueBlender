import bpy,math
from mathutils import Vector
p=r'C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\PurdueBlender\modular\buildings\massing_hillenbrand_hall_a71e418.blend'
bpy.ops.wm.open_mainfile(filepath=p)
obj=bpy.data.objects['Hillenbrand Hall']
center=Vector((-1102.36,-78.33,15.2))
scene=bpy.context.scene
camdata=bpy.data.cameras.new('PreviewCamera'); cam=bpy.data.objects.new('PreviewCamera',camdata); scene.collection.objects.link(cam)
cam.location=center+Vector((175,-190,135)); direction=center-cam.location; cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); camdata.type='ORTHO'; camdata.ortho_scale=210; scene.camera=cam
ld=bpy.data.lights.new('KeyLight','AREA'); lo=bpy.data.objects.new('KeyLight',ld);scene.collection.objects.link(lo);lo.location=center+Vector((40,-60,120));ld.energy=22000;ld.size=100
scene.render.engine='BLENDER_EEVEE'; scene.eevee.taa_render_samples=32
scene.render.resolution_x=1100;scene.render.resolution_y=850;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=r'C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\PurdueBlender\audit\massing_hillenbrand_hall_a71e418\review\preview_before.png'
scene.render.film_transparent=False
bpy.ops.render.render(write_still=True)
