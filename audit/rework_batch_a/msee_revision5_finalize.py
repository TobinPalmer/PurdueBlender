import bpy, os, math, json
from mathutils import Vector
ROOT=os.path.abspath('.'); OUT=os.path.join(ROOT,'audit','rework_batch_a')
ASSET=os.path.join(ROOT,'modular','buildings','materials_science_and_electrical_engineering_msee.blend')
bpy.ops.wm.open_mainfile(filepath=ASSET)
coll=bpy.data.collections['Asset_materials_science_and_electrical_engineering_msee']
screen=bpy.data.objects['MSEE_Max_W_Brown_two_story_glazed_atrium']
pts=[screen.matrix_world@v.co for v in screen.data.vertices]; center=sum(pts,Vector())/len(pts)
t=Vector((.627,-.779,0)).normalized(); inward=Vector((-t.y,t.x,0)); angle=math.atan2(t.y,t.x)
# Remove only punched-window objects in the two-storey glazed atrium panel; adjacent brick-bay windows stay.
removed=[]
for o in list(coll.all_objects):
 if not o.name.startswith(('MSEE_window_3_','MSEE_mullion_3_','MSEE_sill_3_')): continue
 # restrict to first two storeys and the full width of the atrium screen
 ps=[o.matrix_world@Vector(v) for v in o.bound_box]; c=sum(ps,Vector())/8
 tang=(c-center).dot(t); depth=(c-center).dot(inward)
 if abs(tang)<=10.6 and depth<0.8 and depth>-0.7 and c.z<=8.8:
  removed.append(o.name); bpy.data.objects.remove(o,do_unlink=True)
# Cut a two-storey glazed lobby opening through the solid shell. The 18 m depth is a visual interpretation,
# not an as-built dimension; it opens the atrium circulation zone but preserves the far building mass.
depth=18.0; width=22.25; height=8.30
bpy.ops.mesh.primitive_cube_add(size=1,location=center+inward*(depth/2))
cutter=bpy.context.object; cutter.name='TEMP_MSEE_atrium_wall_opening'; cutter.dimensions=(width,depth,height); cutter.rotation_euler[2]=angle
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
shell=bpy.data.objects['materials_science_and_electrical_engineering_msee_official_GIS_shell']
mod=shell.modifiers.new('R5 two-storey atrium opening','BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cutter
bpy.context.view_layer.objects.active=shell; shell.select_set(True); bpy.ops.object.modifier_apply(modifier=mod.name); shell.select_set(False); bpy.data.objects.remove(cutter,do_unlink=True)
# Move the existing atrium study-table vignette behind the glazing, all to one shallow lounge zone.
for o in list(coll.all_objects):
 if o.name.startswith(('R2_MSEE_atrium_collaboration_table_','R2_MSEE_atrium_seat_')):
  d=(o.matrix_world.translation-center).dot(inward); o.location += inward*(2.2-d)
# Reflective but readable glazing, with the source-supported atrium interior visible behind it.
glass=bpy.data.materials['R5_MSEE_brown_atrium_glass']; mix=next(n for n in glass.node_tree.nodes if n.type=='MIX_SHADER'); mix.inputs[0].default_value=.72
# Door panels are transparent tinted glazing too, instead of opaque teal blocks.
door=bpy.data.materials['R5_MSEE_entry_door_glass']; door.node_tree.nodes.clear(); dn=door.node_tree.nodes; dl=door.node_tree.links
p=dn.new('ShaderNodeBsdfPrincipled'); p.inputs['Base Color'].default_value=(.12,.24,.27,1); p.inputs['Roughness'].default_value=.2; p.inputs['Metallic'].default_value=.12
tr=dn.new('ShaderNodeBsdfTransparent'); mx=dn.new('ShaderNodeMixShader'); mx.inputs[0].default_value=.42; out=dn.new('ShaderNodeOutputMaterial')
dl.new(p.outputs['BSDF'],mx.inputs[1]); dl.new(tr.outputs['BSDF'],mx.inputs[2]); dl.new(mx.outputs['Shader'],out.inputs['Surface']); door.surface_render_method='DITHERED'
# Slightly brighter frame allows the source-visible fanlight arch to read behind the glazing.
frame=bpy.data.materials['R5_MSEE_entry_frame']; fp=next(x for x in frame.node_tree.nodes if x.type=='BSDF_PRINCIPLED'); fp.inputs['Base Color'].default_value=(.27,.29,.28,1); fp.inputs['Metallic'].default_value=.48; fp.inputs['Roughness'].default_value=.32; frame.diffuse_color=(.27,.29,.28,1)
# overview render on existing saved scene camera
scene=bpy.context.scene; prevcam=scene.camera
scene.render.engine='CYCLES'; scene.cycles.samples=32; scene.render.resolution_x=1400; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.filepath=os.path.join(OUT,'materials_science_and_electrical_engineering_msee_revision5_preview.png')
bpy.ops.render.render(write_still=True)
# close facade view, then remove its temporary camera before saving the library
loc=center-inward*42+Vector((0,0,8)); target=center+Vector((0,0,3.9))
bpy.ops.object.camera_add(location=loc); cam=bpy.context.object; cam.name='TEMP_MSEE_R5_entry_camera'; cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=60
scene.camera=cam; scene.render.resolution_x=1300; scene.render.resolution_y=900; scene.render.filepath=os.path.join(OUT,'materials_science_and_electrical_engineering_msee_revision5_entry_detail.png'); bpy.ops.render.render(write_still=True)
scene.camera=prevcam; bpy.data.objects.remove(cam,do_unlink=True)
# Save only the assigned MSEE library; footprint/origin/manifest are unchanged.
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print('R5 final saved; objects=',len(coll.all_objects),'shell verts/faces=',len(shell.data.vertices),len(shell.data.polygons),'removed atrium windows=',len(removed))
print('removed names:',json.dumps(removed))
