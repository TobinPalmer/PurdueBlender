import bpy,os
from mathutils import Vector
root=os.path.abspath('.'); out=os.path.join(root,'audit','material_review','roof_visibility_refresh')
items=[('walc','Hipped wing roof'),('felix_haas_hall','HAAS_Hipped_Roof'),('mccutcheon_hall','MCUT_Center_Roof_Main')]
for key,roofname in items:
 bpy.ops.wm.open_mainfile(filepath=os.path.join(root,'modular','buildings',key+'.blend')); sc=bpy.context.scene
 pts=[o.matrix_world@Vector(c) for o in sc.objects if o.type=='MESH' and not o.hide_render and max(o.dimensions)<120 for c in o.bound_box]
 lo=Vector((min(v.x for v in pts),min(v.y for v in pts),min(v.z for v in pts))); hi=Vector((max(v.x for v in pts),max(v.y for v in pts),max(v.z for v in pts))); center=(lo+hi)*.5; size=hi-lo; span=max(size)
 d=bpy.data.cameras.new('RoofReviewCamera'); cam=bpy.data.objects.new('RoofReviewCamera',d); sc.collection.objects.link(cam); cam.location=center+Vector((1,-1,.7))*span*1.6; cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); d.type='ORTHO'; d.ortho_scale=span*2; sc.camera=cam
 sc.render.engine='BLENDER_EEVEE'; sc.render.resolution_x=1100; sc.render.resolution_y=720; sc.render.resolution_percentage=100; sc.render.filepath=os.path.join(out,key+'_overview_eevee.png'); bpy.ops.render.render(write_still=True); print('RENDER',sc.render.filepath)
 roof=bpy.data.objects[roofname]; rp=[roof.matrix_world@Vector(c) for c in roof.bound_box]; rlo=Vector((min(v.x for v in rp),min(v.y for v in rp),min(v.z for v in rp))); rhi=Vector((max(v.x for v in rp),max(v.y for v in rp),max(v.z for v in rp))); rc=(rlo+rhi)*.5; rs=max(rhi-rlo)
 cam.location=rc+Vector((.35,-.55,1.1))*rs*1.1; cam.rotation_euler=(rc-cam.location).to_track_quat('-Z','Y').to_euler(); d.ortho_scale=max(rhi.x-rlo.x,rhi.y-rlo.y)*1.3; sc.render.resolution_x=1100; sc.render.resolution_y=720; sc.render.filepath=os.path.join(out,key+'_roof_close_eevee.png'); bpy.ops.render.render(write_still=True); print('RENDER',sc.render.filepath)
