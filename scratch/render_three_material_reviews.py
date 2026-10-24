import bpy, math, os
from mathutils import Vector
root=os.path.abspath('modular/buildings')
outroot=os.path.abspath('audit/material_pass2')
os.makedirs(outroot,exist_ok=True)
files=('potter_engineering.blend','mechanical_engineering.blend','electrical_engineering.blend')
for filename in files:
    bpy.ops.wm.open_mainfile(filepath=os.path.join(root,filename))
    scene=bpy.context.scene
    mesh=[o for o in scene.objects if o.type=='MESH' and not o.hide_render]
    pts=[o.matrix_world @ Vector(c) for o in mesh for c in o.bound_box]
    lo=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    hi=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    center=(lo+hi)*0.5; span=max(hi-lo)
    cd=bpy.data.cameras.new('MaterialReviewCamera'); cam=bpy.data.objects.new('MaterialReviewCamera',cd); scene.collection.objects.link(cam)
    cam.location=center+Vector((1.5,-2.0,1.35))*span
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); cd.type='ORTHO'; cd.ortho_scale=span*1.65; scene.camera=cam
    ld=bpy.data.lights.new('MaterialReviewArea','AREA'); light=bpy.data.objects.new('MaterialReviewArea',ld); scene.collection.objects.link(light)
    light.location=center+Vector((-0.7,-1.0,1.5))*span; ld.energy=span*span*16; ld.shape='DISK'; ld.size=span*.9
    light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
    if scene.world: scene.world.color=(0.12,0.16,0.22)
    scene.render.engine='CYCLES'; scene.cycles.samples=16
    scene.render.resolution_x=900; scene.render.resolution_y=650; scene.render.resolution_percentage=70
    scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(outroot,filename.replace('.blend','.png'))
    scene.view_settings.view_transform='AgX'
    bpy.ops.render.render(write_still=True)
    print('RENDERED',scene.render.filepath)
