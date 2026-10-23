import bpy,math,pathlib
from mathutils import Vector,Matrix
P=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');A=P/'audit/batch3_elliott';src=P/'modular/buildings/elliott_hall_of_music.blend';bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;c=bpy.data.collections['Asset_elliott_hall_of_music'];t=Vector((.63281,-.77431,0));n=Vector((.77431,.63281,0));z=Vector((0,0,1));ctr=Vector((44.075,9.162,5.72));rot=Matrix(((t.x,n.x,z.x,ctr.x),(t.y,n.y,z.y,ctr.y),(0,0,1,ctr.z),(0,0,0,1)))
bpy.ops.mesh.primitive_cube_add(size=1);cut=bpy.context.object;cut.name='TEMP_R10_Wider_Portal_Trim_Cutter';cut.matrix_world=rot@Matrix.Diagonal((3.55,4.2,3.5,1));objects=['ELLT_R6_Continuous_Limestone_Belt_Courses_Estimated','ELLT_R6_Continuous_Limestone_Belt_Courses_Estimated.001']
for name in objects:
 o=bpy.data.objects.get(name)
 if not o:continue
 m=o.modifiers.new('R10_Widen_Trim_Clearance_At_Portal','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name);o['round10_portal_clearance']='Belt course locally clipped across modeled door width; width is estimated, opening does not imply accessibility compliance.'
bpy.data.objects.remove(cut,do_unlink=True);bpy.ops.wm.save_as_mainfile(filepath=str(src))
# Render temporary evidence view.
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=48;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0
ld=bpy.data.lights.new('TEMP_R10_Key','AREA');ld.energy=1600;ld.shape='DISK';ld.size=10;l=bpy.data.objects.new('TEMP_R10_Key',ld);s.collection.objects.link(l);l.location=(58,21,13);l.rotation_euler=(Vector((44.1,9.2,5.8))-l.location).to_track_quat('-Z','Y').to_euler();camd=bpy.data.cameras.new('TEMP_R10_Camera');camd.type='ORTHO';camd.ortho_scale=17.5;cam=bpy.data.objects.new('TEMP_R10_Camera',camd);s.collection.objects.link(cam);cam.location=(58,21,11);cam.rotation_euler=(Vector((44.1,9.2,5.8))-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam;s.render.resolution_x=1600;s.render.resolution_y=1050;s.render.resolution_percentage=100;s.render.filepath=str(A/'entry_portal_round10.png');bpy.ops.render.render(write_still=True)
print('R10 wider opening pass saved',sum(o.type=='MESH' for o in c.objects))
