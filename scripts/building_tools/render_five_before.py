import bpy,os
from mathutils import Vector
files=['south_hall','stewart_center','tarkington_hall','university_hall','walc'];os.makedirs('audit/material_review/pass2_before',exist_ok=True)
for f in files:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(f'modular/buildings/{f}.blend')); sc=bpy.context.scene
 pts=[o.matrix_world@Vector(c) for o in bpy.data.objects if o.type=='MESH' and max(o.dimensions)<120 for c in o.bound_box]
 lo=Vector((min(v.x for v in pts),min(v.y for v in pts),min(v.z for v in pts)));hi=Vector((max(v.x for v in pts),max(v.y for v in pts),max(v.z for v in pts)));center=(lo+hi)*.5;size=hi-lo
 d=bpy.data.cameras.new('ReviewCamera');cam=bpy.data.objects.new('ReviewCamera',d);sc.collection.objects.link(cam);cam.location=center+Vector((1,-1,0.7))*max(size)*1.6;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=max(size)*2.0;sc.camera=cam
 sc.render.engine='BLENDER_EEVEE';sc.render.resolution_x=700;sc.render.resolution_y=500;sc.render.resolution_percentage=100;sc.render.filepath=os.path.abspath(f'audit/material_review/pass2_before/{f}.png');bpy.ops.render.render(write_still=True);print('rendered',f)
