import bpy, math, os
from mathutils import Vector
src=os.path.abspath('modular/buildings/potter_engineering.blend')
out=os.path.abspath('audit/potter_material_after.png')
bpy.ops.wm.open_mainfile(filepath=src)
scene=bpy.context.scene
mesh=[o for o in scene.objects if o.type=='MESH' and not o.hide_render]
pts=[o.matrix_world @ Vector(c) for o in mesh for c in o.bound_box]
lo=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
hi=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
center=(lo+hi)*0.5
span=max(hi-lo)
cam_data=bpy.data.cameras.new('ReviewCamera'); cam=bpy.data.objects.new('ReviewCamera',cam_data); scene.collection.objects.link(cam)
cam.location=center+Vector((1.5,-2.0,1.35))*span
direction=center-cam.location; cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); cam_data.type='ORTHO'; cam_data.ortho_scale=span*1.65; scene.camera=cam
ld=bpy.data.lights.new('ReviewArea','AREA'); light=bpy.data.objects.new('ReviewArea',ld); scene.collection.objects.link(light)
light.location=center+Vector((-0.7,-1.0,1.5))*span; ld.energy=span*span*16; ld.shape='DISK'; ld.size=span*0.9; light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
scene.world.color=(0.12,0.16,0.22)
scene.render.engine='CYCLES'; scene.cycles.samples=24
scene.render.resolution_x=900; scene.render.resolution_y=650; scene.render.resolution_percentage=80
scene.render.image_settings.file_format='PNG'; scene.render.filepath=out
scene.view_settings.view_transform='AgX'
bpy.ops.render.render(write_still=True)
print('RENDERED',out)
