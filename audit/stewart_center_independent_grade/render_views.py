import bpy, pathlib
from mathutils import Vector
scene=bpy.context.scene
col=bpy.data.collections['Asset_stewart_center']
pts=[o.matrix_world @ Vector(corner) for o in col.all_objects if o.type in {'MESH','CURVE','FONT'} for corner in o.bound_box]
center=Vector((-5,-4,8))
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1500; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.view_settings.view_transform='Standard'; scene.view_settings.look='Medium High Contrast'
if scene.world is None: scene.world=bpy.data.worlds.new('Stewart_review_world')
scene.world.use_nodes=True; scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(0.17,0.2,0.26,1); scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.35
ld=bpy.data.lights.new('Stewart_review_key','AREA'); ld.energy=4500; ld.shape='DISK'; ld.size=100
lo=bpy.data.objects.new('Stewart_review_key',ld); scene.collection.objects.link(lo); lo.location=center+Vector((45,-85,100)); lo.rotation_euler=(center-lo.location).to_track_quat('-Z','Y').to_euler()
views=[('south_oblique',center+Vector((135,-160,105))),('north_oblique',center+Vector((-145,145,120))),('top',center+Vector((0,0,250)))]
out=pathlib.Path(__file__).resolve().parent; out.mkdir(parents=True,exist_ok=True)
for name,loc in views:
 cd=bpy.data.cameras.new('Stewart_review_'+name); cam=bpy.data.objects.new('Stewart_review_'+name,cd); scene.collection.objects.link(cam)
 cam.location=loc; cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); cd.lens=55; scene.camera=cam
 if name=='top': cd.type='ORTHO'; cd.ortho_scale=185
 scene.render.filepath=str(out/f'{name}.png'); bpy.ops.render.render(write_still=True); print('rendered',name)




