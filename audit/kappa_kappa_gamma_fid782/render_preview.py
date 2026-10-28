import bpy, math, os
from mathutils import Vector
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
path=os.path.join(ROOT,'modular','buildings','massing_house_301840871_5d1bc06.blend')
outdir=os.path.dirname(__file__)
bpy.ops.wm.open_mainfile(filepath=path)
scene=bpy.context.scene
target=bpy.data.objects.get('House_301840871')
for ob in list(bpy.data.objects):
 if ob!=target:bpy.data.objects.remove(ob,do_unlink=True)
center=Vector((-391.8,63.3,4.3))
camera_data=bpy.data.cameras.new('KKG Preview Camera'); camera=bpy.data.objects.new('KKG Preview Camera',camera_data); scene.collection.objects.link(camera)
camera.data.type='ORTHO';camera.data.ortho_scale=52
camera.location=center+Vector((42,-30,23)); direction=center-camera.location; camera.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); scene.camera=camera
for name,loc,power,size in [('Key',(-350,42,28),1300,22),('Fill',(-374,105,18),600,18)]:
 d=bpy.data.lights.new(name,'AREA');o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;d.energy=power;d.shape='DISK';d.size=size;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='WORLD'
scene.render.image_settings.file_format='PNG';scene.render.filepath=os.path.join(outdir,'exterior_preview.png')
scene.world.use_nodes=True
bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.22,.28,.36,1);bg.inputs['Strength'].default_value=.3
bpy.ops.render.render(write_still=True)
scene.render.filepath=os.path.join(outdir,'exterior_courtyard.png')
camera.location=center+Vector((10,-48,25)); direction=center-camera.location; camera.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
bpy.ops.render.render(write_still=True)
camera.location=center+Vector((0,0,62));camera.rotation_euler=(0,0,0)
camera.rotation_euler=(0,0,0)
# camera looks along local -Z; top view needs X rotation 0 and camera roll 0.
scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.camera=camera
scene.render.filepath=os.path.join(outdir,'top_preview.png');bpy.ops.render.render(write_still=True)
# Tight view documents the source-visible centered chapter entry treatment.
entry_center=Vector((-390.97,65.01,4.0));camera.data.ortho_scale=12
camera.location=entry_center+Vector((28,0,4));camera.rotation_euler=(entry_center-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.camera=camera
scene.render.filepath=os.path.join(outdir,'entrance_detail.png');bpy.ops.render.render(write_still=True)
print('RENDERED',outdir)
