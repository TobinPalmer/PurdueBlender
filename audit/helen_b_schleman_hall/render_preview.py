import bpy, json, os
from mathutils import Vector
here=os.path.dirname(__file__)
cfg=json.load(open(os.path.join(here,'build_config.json'),encoding='utf8'))
obj=bpy.data.objects.get(cfg['object_name'])
if obj is None: raise RuntimeError('Target asset missing')
verts=[obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
lo=Vector(tuple(min(v[i] for v in verts) for i in range(3))); hi=Vector(tuple(max(v[i] for v in verts) for i in range(3)))
center=(lo+hi)*0.5; size=max(hi-lo); cam_data=bpy.data.cameras.new('PreviewCamera'); cam=bpy.data.objects.new('PreviewCamera',cam_data); bpy.context.scene.collection.objects.link(cam)
cam.location=center+Vector((-size*1.4,-size*1.35,size*0.58)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); cam_data.type='ORTHO'; cam_data.ortho_scale=size*1.5; bpy.context.scene.camera=cam
for name,loc,power,area in [('Key',center+Vector((-size,-size,size*2)),size*size*0.12,size*1.2),('Fill',center+Vector((size,size*0.6,size)),size*size*0.045,size*1.5)]:
 ld=bpy.data.lights.new(name,'AREA'); ld.energy=power; ld.shape='DISK'; ld.size=area; lo_obj=bpy.data.objects.new(name,ld); bpy.context.scene.collection.objects.link(lo_obj); lo_obj.location=loc; lo_obj.rotation_euler=(center-loc).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene; gmat=bpy.data.materials.new('PreviewGround'); gmat.diffuse_color=(0.20,0.24,0.16,1); gmat.use_nodes=True; gmat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(0.20,0.24,0.16,1); bpy.ops.mesh.primitive_plane_add(size=220,location=(center.x,center.y,-0.04)); bpy.context.object.name='PreviewGround'; bpy.context.object.data.materials.append(gmat); scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1440; scene.render.resolution_y=1080; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False; scene.render.resolution_percentage=100; scene.eevee.taa_render_samples=64
scene.world.color=(0.035,0.035,0.035); scene.view_settings.view_transform='AgX'; scene.view_settings.exposure=-0.55; scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(here,'preview_detail.png'); scene.camera.data.lens=50
bpy.ops.render.render(write_still=True)
print('PREVIEW_RENDER='+scene.render.filepath)
