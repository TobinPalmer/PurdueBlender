import bpy, os
from mathutils import Vector
root=os.path.abspath('.'); out=os.path.join(root,'audit','material_review','roof_visibility_refresh')
bpy.ops.wm.open_mainfile(filepath=os.path.join(root,'modular','buildings','walc.blend')); sc=bpy.context.scene
for o in bpy.data.objects:
 if o.type=='MESH' and o.name!='WALC_Official_906_Roof': o.hide_render=True
roof=bpy.data.objects['WALC_Official_906_Roof']; pts=[roof.matrix_world@Vector(c) for c in roof.bound_box]; lo=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts))); hi=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts))); c=(lo+hi)*.5; span=max(hi-lo)
d=bpy.data.cameras.new('WALC Roof Isolated'); cam=bpy.data.objects.new('WALC Roof Isolated',d); sc.collection.objects.link(cam); cam.location=c+Vector((.12,-.1,1))*span*2; cam.rotation_euler=(c-cam.location).to_track_quat('-Z','Y').to_euler(); d.type='ORTHO'; d.ortho_scale=span*1.25; sc.camera=cam
sc.render.engine='BLENDER_EEVEE'; sc.render.resolution_x=1200; sc.render.resolution_y=800; sc.render.resolution_percentage=100; sc.render.filepath=os.path.join(out,'walc_reference_roof_isolated.png'); bpy.ops.render.render(write_still=True); print('MATERIAL',roof.material_slots[0].material.name,'FILE',sc.render.filepath)
