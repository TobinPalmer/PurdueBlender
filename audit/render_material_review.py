import bpy, sys, os, math
from mathutils import Vector
paths=sys.argv[sys.argv.index('--')+1:]
for p in paths:
 bpy.ops.wm.open_mainfile(filepath=p)
 # include visible mesh geometry and bound it
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.visible_get()]
 pts=[o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
 if not pts: continue
 mn=Vector((min(v.x for v in pts),min(v.y for v in pts),min(v.z for v in pts))); mx=Vector((max(v.x for v in pts),max(v.y for v in pts),max(v.z for v in pts)))
 c=(mn+mx)*.5; dims=mx-mn; radius=max(dims.length*.65,5)
 camdata=bpy.data.cameras.new('AuditCamera'); cam=bpy.data.objects.new('AuditCamera',camdata); bpy.context.scene.collection.objects.link(cam)
 cam.location=c+Vector((-radius*1.3,-radius*1.5,radius*.75)); cam.rotation_euler=(c-cam.location).to_track_quat('-Z','Y').to_euler(); camdata.lens=55; bpy.context.scene.camera=cam
 # consistent neutral studio lighting
 w=bpy.context.scene.world or bpy.data.worlds.new('AuditWorld'); bpy.context.scene.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs['Color'].default_value=(.22,.27,.34,1); w.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
 for name,loc,power,size in [('Key',c+Vector((-radius,-radius,radius*1.2)),2500,radius*.8),('Fill',c+Vector((radius,-radius*.1,radius*.4)),900,radius*.7)]:
  ld=bpy.data.lights.new(name,'AREA'); lo=bpy.data.objects.new(name,ld); bpy.context.scene.collection.objects.link(lo); lo.location=loc; ld.energy=power; ld.shape='DISK'; ld.size=size; lo.rotation_euler=(c-lo.location).to_track_quat('-Z','Y').to_euler()
 sc=bpy.context.scene; sc.render.engine='BLENDER_EEVEE'; sc.eevee.taa_render_samples=16; sc.render.resolution_x=800; sc.render.resolution_y=600; sc.render.resolution_percentage=100
 sc.view_settings.view_transform='AgX'; sc.render.image_settings.file_format='PNG'; sc.render.filepath=os.path.abspath('audit/material_review_'+os.path.splitext(os.path.basename(p))[0]+'.png')
 bpy.ops.render.render(write_still=True); print('RENDERED',sc.render.filepath, 'DIMS',tuple(round(x,1) for x in dims))
