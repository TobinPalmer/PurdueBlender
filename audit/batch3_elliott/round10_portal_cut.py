import bpy, math, pathlib, json
from mathutils import Vector, Matrix
P=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); A=P/'audit/batch3_elliott'; src=P/'modular/buildings/elliott_hall_of_music.blend'; bpy.ops.wm.open_mainfile(filepath=str(src)); s=bpy.context.scene; c=bpy.data.collections['Asset_elliott_hall_of_music']
# Confirm prior round10 material edit exists and keep it as an opaque, non-glinty tinted glass approximation.
glass=bpy.data.materials['ELLT_R8_Door_Glass_Estimated']; bsdf=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); bsdf.inputs['Roughness'].default_value=.68; bsdf.inputs['Specular IOR Level'].default_value=.12; bsdf.inputs['Transmission Weight'].default_value=0
# Cut the continuous limestone belt course that intruded through the entrance door leaf.
# Door width/height are estimates; the cut is constrained to the portal, not the façade wall.
t=Vector((.63281,-.77431,0)); n=Vector((.77431,.63281,0)); z=Vector((0,0,1)); center=Vector((44.075,9.162,5.72))
mat=Matrix(((t.x,n.x,z.x,center.x),(t.y,n.y,z.y,center.y),(t.z,n.z,z.z,center.z),(0,0,0,1)))
bpy.ops.mesh.primitive_cube_add(size=1, location=center); cutter=bpy.context.object; cutter.name='TEMP_R10_Portal_Trim_Cutter'; cutter.dimensions=(2.22,4.0,3.34); cutter.matrix_world=mat@Matrix.Diagonal((2.22,4.0,3.34,1)); bpy.context.view_layer.objects.active=cutter; cutter.select_set(False)
cut_names=[]
for name in ['ELLT_R6_Continuous_Limestone_Belt_Courses_Estimated','ELLT_R6_Continuous_Limestone_Belt_Courses_Estimated.001']:
 o=bpy.data.objects.get(name)
 if not o:continue
 mod=o.modifiers.new('R10_Clear_Trim_From_Upper_Portal','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name);o.select_set(False);cut_names.append(name)
bpy.data.objects.remove(cutter,do_unlink=True)
# Record that these openings are portal-specific and estimated.
for name in cut_names:bpy.data.objects[name]['round10_note']='Portal-specific clearance cut; portal dimensions estimated. Continuous limestone belt no longer intersects the door leaf.'
bpy.data.objects['ELLT_R8_Elliott_Side_Interface_Landing_Estimated']['interface_status']='Elliott-only provisional landing. Hovde portal/connector unverified; GIS footprint contact does not establish an upper-level route.'
bpy.ops.wm.save_as_mainfile(filepath=str(src))
# Render clean/wide entry detail as a review image with temporary lighting/camera.
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=48;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0
ld=bpy.data.lights.new('TEMP_R10_Entry_Key','AREA');ld.energy=1600;ld.shape='DISK';ld.size=10;l=bpy.data.objects.new('TEMP_R10_Entry_Key',ld);s.collection.objects.link(l);l.location=(55,20,14);l.rotation_euler=(Vector((44,9,5.8))-l.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('TEMP_R10_Entry_Camera');camd.type='ORTHO';camd.ortho_scale=17.5;cam=bpy.data.objects.new('TEMP_R10_Entry_Camera',camd);s.collection.objects.link(cam);cam.location=(58,21,11);cam.rotation_euler=(Vector((44.1,9.2,5.8))-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam
s.render.resolution_x=1600;s.render.resolution_y=1050;s.render.resolution_percentage=100;s.render.filepath=str(A/'entry_portal_round10.png');bpy.ops.render.render(write_still=True)
# One pixel-aligned ray through the left-leaf area verifies the limestone obstruction is gone.
dg=bpy.context.evaluated_depsgraph_get();target=Vector((44.075,9.162,5.2));origin=Vector((58,21,5.2));direction=(target-origin).normalized();ok,hit,norm,face,ob,mat_hit=s.ray_cast(dg,origin,direction);print(json.dumps({'cut_course_objects':cut_names,'door_leaf_ray_first_hit':ob.name if ob else None,'hit_point':tuple(round(x,3) for x in hit),'mesh_count':sum(o.type=='MESH' for o in c.objects)}))
# Remove render-only items from the current scene (asset was saved before these were added).
for o in (cam,l):
 data=o.data;bpy.data.objects.remove(o,do_unlink=True)
 if data.users==0:(bpy.data.cameras if data.type=='CAMERA' else bpy.data.lights).remove(data)
