import bpy, json, os
from mathutils import Vector
here=os.path.dirname(__file__)
cfg=json.load(open(os.path.join(here,'build_config.json'),encoding='utf8'))
obj=bpy.data.objects.get(cfg['object_name'])
if obj is None: raise RuntimeError('Target asset missing')
verts=[obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
lo=Vector(tuple(min(v[i] for v in verts) for i in range(3))); hi=Vector(tuple(max(v[i] for v in verts) for i in range(3)))
center=(lo+hi)*0.5; size=max(hi-lo); cam_data=bpy.data.cameras.new('PreviewCamera'); cam=bpy.data.objects.new('PreviewCamera',cam_data); bpy.context.scene.collection.objects.link(cam)
cam.location=center+Vector((-size*1.4,-size*1.35,size*0.9)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); cam_data.type='ORTHO'; cam_data.ortho_scale=size*1.5; bpy.context.scene.camera=cam
for name,loc,power,area in [('Key',center+Vector((-size,-size,size*2)),size*size*0.45,size*1.2),('Fill',center+Vector((size,size*0.6,size)),size*size*0.18,size*1.5)]:
 ld=bpy.data.lights.new(name,'AREA'); ld.energy=power; ld.shape='DISK'; ld.size=area; lo_obj=bpy.data.objects.new(name,ld); bpy.context.scene.collection.objects.link(lo_obj); lo_obj.location=loc; lo_obj.rotation_euler=(center-loc).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene; scene.render.engine='BLENDER_WORKBENCH'; scene.display.shading.light='STUDIO'; scene.display.shading.color_type='MATERIAL'; scene.display.shading.studio_light='paint.sl'; scene.display.shading.show_shadows=True; scene.display.shading.show_cavity=True; scene.display.shading.cavity_type='BOTH'; scene.render.resolution_x=1120; scene.render.resolution_y=840; scene.render.resolution_percentage=100
scene.world.color=(0.035,0.035,0.035); scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(here,'preview_detail_r2.png'); scene.camera.data.lens=50
bpy.ops.render.render(write_still=True)
print('PREVIEW_RENDER='+scene.render.filepath)

# Entrance elevation and plan overview are separate evidence views.
cam.location=center+Vector((-size*1.8,0.0,size*0.22)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); cam_data.ortho_scale=size*1.32
scene.render.filepath=os.path.join(here,'preview_entrance_r1.png'); bpy.ops.render.render(write_still=True); print('PREVIEW_RENDER='+scene.render.filepath)
cam.location=center+Vector((0.0,0.0,size*2.5)); cam.rotation_euler=(0.0,0.0,0.0); cam_data.ortho_scale=size*1.3
scene.render.filepath=os.path.join(here,'preview_top_r1.png'); bpy.ops.render.render(write_still=True); print('PREVIEW_RENDER='+scene.render.filepath)
