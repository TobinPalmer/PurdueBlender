import bpy, json, os
from mathutils import Vector
here=os.path.dirname(__file__); cfg=json.load(open(os.path.join(here,'build_config.json'),encoding='utf8')); obj=bpy.data.objects.get(cfg['object_name'])
if obj is None: raise RuntimeError('Slayter object missing')
world=[obj.matrix_world@Vector(p) for p in obj.bound_box]; lo=Vector(tuple(min(v[i] for v in world) for i in range(3))); hi=Vector(tuple(max(v[i] for v in world) for i in range(3))); center=(lo+hi)*.5; size=max(hi-lo)
cd=bpy.data.cameras.new('SlayterPreviewCamera'); cam=bpy.data.objects.new('SlayterPreviewCamera',cd); bpy.context.scene.collection.objects.link(cam); cam.location=center+Vector((size*1.55,-size*1.30,size*.9)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); cd.type='ORTHO'; cd.ortho_scale=size*1.50; bpy.context.scene.camera=cam
for name,loc,power,area in [('Key',center+Vector((size,-size,size*2)),size*size*.08,size*1.1),('Fill',center+Vector((-size,size*.6,size)),size*size*.03,size*1.4)]:
 ld=bpy.data.lights.new(name,'AREA'); ld.energy=power; ld.shape='DISK'; ld.size=area; light=bpy.data.objects.new(name,ld); bpy.context.scene.collection.objects.link(light); light.location=loc; light.rotation_euler=(center-loc).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene; scene.render.engine='BLENDER_WORKBENCH'; scene.display.shading.light='STUDIO'; scene.display.shading.color_type='MATERIAL'; scene.display.shading.studio_light='paint.sl'; scene.display.shading.show_shadows=True; scene.display.shading.show_cavity=True; scene.display.shading.cavity_type='BOTH'; scene.render.resolution_x=1120; scene.render.resolution_y=840; scene.render.resolution_percentage=100; scene.world.color=(.035,.035,.035); scene.view_settings.view_transform='Standard'; scene.view_settings.look='Medium High Contrast'; scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(here,'preview_detail.png'); bpy.ops.render.render(write_still=True)
print('PREVIEW_RENDER='+scene.render.filepath)


