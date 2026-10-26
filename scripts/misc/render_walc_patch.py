import bpy,os
from mathutils import Vector
p=os.path.abspath(r'modular/buildings/walc.blend');bpy.ops.wm.open_mainfile(filepath=p);sc=bpy.context.scene
roof=bpy.data.objects['Hipped wing roof']; center=roof.matrix_world.translation.copy(); center.z+=2
for o in bpy.data.objects:
 if o.type=='MESH' and o!=roof:o.hide_render=True
# Camera down onto a patch of roofing, keeping the local material graph under review.
d=bpy.data.cameras.new('RoofReview');cam=bpy.data.objects.new('RoofReview',d);sc.collection.objects.link(cam);cam.location=center+Vector((4,-6,22));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=14;sc.camera=cam
sc.render.engine='BLENDER_EEVEE';sc.render.resolution_x=400;sc.render.resolution_y=300;sc.render.filepath=os.path.abspath('audit/material_review/pass2_after/walc_roof_close.png');bpy.ops.render.render(write_still=True);print('rendered WALC roof patch')
