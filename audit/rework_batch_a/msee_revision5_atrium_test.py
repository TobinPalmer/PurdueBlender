import bpy, os, math
from mathutils import Vector
ROOT=os.path.abspath('.'); asset=os.path.join(ROOT,'modular','buildings','materials_science_and_electrical_engineering_msee.blend')
bpy.ops.wm.open_mainfile(filepath=asset)
coll=bpy.data.collections['Asset_materials_science_and_electrical_engineering_msee']
screen=bpy.data.objects['MSEE_Max_W_Brown_two_story_glazed_atrium']; pts=[screen.matrix_world@v.co for v in screen.data.vertices]; center=sum(pts,Vector())/len(pts)
t=Vector((.627,-.779,0)).normalized(); inward=Vector((-t.y,t.x,0)); angle=math.atan2(t.y,t.x)
# Cut a two-storey atrium opening through the solid front wall, stopping inside the lobby.
# Width is matched to the documented glass atrium. Depth/height are approximate, not a measured plan.
depth=18.0; width=22.25; height=8.30
bpy.ops.mesh.primitive_cube_add(size=1, location=center+inward*(depth/2))
cutter=bpy.context.object; cutter.name='TEMP_MSEE_atrium_wall_opening'
cutter.dimensions=(width,depth,height); cutter.rotation_euler[2]=angle
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
# Boolean only the named GIS massing shell; retain its location and collection placement.
shell=bpy.data.objects['materials_science_and_electrical_engineering_msee_official_GIS_shell']
mod=shell.modifiers.new('R5 two-storey atrium opening','BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cutter
bpy.context.view_layer.objects.active=shell; shell.select_set(True); bpy.ops.object.modifier_apply(modifier=mod.name); shell.select_set(False)
bpy.data.objects.remove(cutter,do_unlink=True)
# Place the previously exterior-reading study vignette 2.2 m inside the glazed frontage.
for o in list(coll.all_objects):
 if o.name.startswith(('R2_MSEE_atrium_collaboration_table_','R2_MSEE_atrium_seat_')):
  d=(o.matrix_world.translation-center).dot(inward); o.location += inward*(2.2-d)
# Permit the documented atrium and schematic lounge cues to read through the glazing.
mat=bpy.data.materials['R5_MSEE_brown_atrium_glass']
mix=next(n for n in mat.node_tree.nodes if n.type=='MIX_SHADER'); mix.inputs[0].default_value=.66
# Close view from exterior (negative inward); full shell and all retained interior detail remain in file.
loc=center-inward*42+Vector((0,0,8)); target=center+Vector((0,0,3.9))
bpy.ops.object.camera_add(location=loc); cam=bpy.context.object; cam.name='TEMP_MSEE_entry_cut_test'; cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=60
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=32; scene.render.resolution_x=1300; scene.render.resolution_y=900; scene.render.resolution_percentage=100; scene.render.filepath=os.path.join(ROOT,'audit','rework_batch_a','materials_science_and_electrical_engineering_msee_revision5_entry_detail.png')
bpy.ops.render.render(write_still=True)
print('test opening applied in memory, shell vertices/faces',len(shell.data.vertices),len(shell.data.polygons),'R2 furniture in atrium',sum(1 for o in coll.all_objects if o.name.startswith('R2_MSEE_atrium_collaboration_table_')))
