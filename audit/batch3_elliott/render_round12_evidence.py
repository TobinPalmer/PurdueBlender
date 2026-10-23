import bpy,pathlib,math,bmesh
from mathutils import Vector,Euler
P=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');A=P/'audit/batch3_elliott';src=P/'modular/buildings/elliott_hall_of_music.blend';bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;c=bpy.data.collections['Asset_elliott_hall_of_music']
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=64;s.render.resolution_x=1600;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.25
if s.world and s.world.use_nodes:
 bg=s.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.5,.53,.58,1);bg.inputs['Strength'].default_value=.85
ld=bpy.data.lights.new('TEMP_R12_Fill','AREA');ld.energy=38000;ld.shape='DISK';ld.size=38;li=bpy.data.objects.new('TEMP_R12_Fill',ld);s.collection.objects.link(li);li.location=(0,0,28);li.rotation_euler=(Vector((0,0,6))-li.location).to_track_quat('-Z','Y').to_euler()
# Render main-floor plan using temporary cut-down copies of merged auditorium meshes.
main_allow=set()
for base in ('ELLT_B3_seat','ELLT_B3_frame','ELLT_B3_carpet','ELLT_B3_stair'):
 orig=bpy.data.objects[base]; dup=orig.copy();dup.data=orig.data.copy();dup.name='TEMP_R12_MAIN_'+base;s.collection.objects.link(dup)
 bm=bmesh.new();bm.from_mesh(dup.data);faces=[f for f in bm.faces if sum(v.co.z for v in f.verts)/len(f.verts)>5.2]
 if faces:bmesh.ops.delete(bm,geom=faces,context='FACES')
 loose=[v for v in bm.verts if not v.link_faces]
 if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
 bm.to_mesh(dup.data);bm.free();main_allow.add(dup.name)
main_allow.add('ELLT_B3_stage');main_allow.update(o.name for o in c.objects if o.name.startswith('ELLT_R12_Pit_Lift_'));main_allow.add(li.name)
for o in s.objects:o.hide_render=(o.name not in main_allow)
camd=bpy.data.cameras.new('TEMP_R12_MAIN_PLAN_CAM');camd.type='ORTHO';camd.ortho_scale=68;cam=bpy.data.objects.new('TEMP_R12_MAIN_PLAN_CAM',camd);s.collection.objects.link(cam);cam.location=(0,0,100);q=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y');cam.rotation_euler=(q@Euler((0,0,math.radians(140.64)),'XYZ').to_quaternion()).to_euler();s.camera=cam;s.render.filepath=str(A/'interior_main_floor_plan_round12.png');bpy.ops.render.render(write_still=True)
# Legible stage-to-audience cutaway, all auditorium geometry except ceiling tiles/wall shell.
allowed={o.name for o in c.objects if o.name.startswith('ELLT_B3_') or o.name.startswith('ELLT_R12_')};allowed={n for n in allowed if not any(t in n.lower() for t in ('ceiling','plaster','wall','light','glow'))};allowed.add(li.name)
for o in s.objects:o.hide_render=(o.name not in allowed)
s.render.resolution_y=1050;cam.location=(22,29,13);camd.ortho_scale=66;cam.rotation_euler=(Vector((-8,-8,6.5))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(A/'interior_central_aisle_round12.png');bpy.ops.render.render(write_still=True)
