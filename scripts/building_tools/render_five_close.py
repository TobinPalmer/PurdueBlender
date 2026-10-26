import bpy,os
from mathutils import Vector
items=[('south_hall',r'modular/buildings/south_hall.blend','SouthHall_Rooftop_Mechanical_Penthouse'),('stewart_center',r'modular/buildings/stewart_center.blend','STEW_Roof_Membrane_Main'),('tarkington_hall',r'modular/buildings/tarkington_hall.blend','Tark_Commons_Hub_Roof_Membrane'),('university_hall',r'modular/buildings/university_hall.blend','UNIV_Mansard_Roof_Deck'),('walc',r'modular/buildings/walc.blend','Hipped wing roof')]
os.makedirs('audit/material_review/pass2_after',exist_ok=True)
for label,p,oname in items:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p));sc=bpy.context.scene;o=bpy.data.objects.get(oname)
 if not o: print('missing',oname);continue
 pts=[o.matrix_world@Vector(c) for c in o.bound_box];lo=Vector((min(v.x for v in pts),min(v.y for v in pts),min(v.z for v in pts)));hi=Vector((max(v.x for v in pts),max(v.y for v in pts),max(v.z for v in pts)));center=(lo+hi)*.5;size=hi-lo
 d=bpy.data.cameras.new('RoofReview');cam=bpy.data.objects.new('RoofReview',d);sc.collection.objects.link(cam);cam.location=center+Vector((.35,-.55,1.1))*max(size)*1.1;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=max(size.x,size.y)*1.3;sc.camera=cam
 sc.render.engine='BLENDER_EEVEE';sc.render.resolution_x=700;sc.render.resolution_y=500;sc.render.resolution_percentage=100;sc.render.filepath=os.path.abspath(f'audit/material_review/pass2_after/{label}_roof_close.png');bpy.ops.render.render(write_still=True);print('rendered close',label)
