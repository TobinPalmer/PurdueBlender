import bpy
from mathutils import Vector
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');bpy.ops.wm.open_mainfile(filepath=str(P/'modular/buildings/hovde_hall.blend'));s=bpy.context.scene;c=bpy.data.collections['Asset_hovde_hall'];s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=72;s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.3
root=bpy.data.objects['HOVD_Root'];entry=bpy.data.objects['HOVD_Portico_Entablature'].matrix_world.translation.copy();target=entry+Vector((0,0,-1));side=(root.matrix_world.to_3x3()@Vector((1,0,0))).normalized();along=(root.matrix_world.to_3x3()@Vector((0,1,0))).normalized()
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def camera(name,loc,t,scale):
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;aim(o,t);d.type='ORTHO';d.ortho_scale=scale;s.camera=o;return o
def light(name,loc,t,power,size):
 d=bpy.data.lights.new(name,'AREA');o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;d.energy=power;d.shape='DISK';d.size=size;aim(o,t)
light('R4_Key',target+side*40+along*27+Vector((0,0,50)),target,1800,45);light('R4_Fill',target-side*32-along*7+Vector((0,0,26)),target,1200,48);light('R4_Rim',target+along*55+Vector((0,0,36)),target,900,44)
cam=camera('R4_Hovde_Wide',target+side*72+along*22+Vector((0,0,23)),target,96);s.render.filepath=str(P/'audit/batch3_hovde/exterior_round4.png');bpy.ops.render.render(write_still=True)
# Human-height close three-quarter view of the revised portico, its columns, and the adjacent windows.
port=bpy.data.objects['HOVD_Portico_Entablature'].matrix_world.translation.copy()+Vector((0,0,-4.7));cam.location=port+side*28+along*4+Vector((0,0,9));aim(cam,port);cam.data.ortho_scale=29;s.render.filepath=str(P/'audit/batch3_hovde/portico_detail_round4.png');bpy.ops.render.render(write_still=True)
# Top-down furniture plans provide a clear read of each modeled room and the remaining circulation area.
for tag,floorname in [('Pres','HOVD_Pres_Floor'),('Board','HOVD_Board_Floor')]:
 floor=bpy.data.objects[floorname];center=floor.matrix_world.translation.copy();cy=-25 if tag=='Pres' else 25
 for o in c.all_objects:
  if not o:continue
  o.hide_render=True
  include=o.name==floorname
  if tag=='Pres': include=include or o.name.startswith(('HOVD_Pres_Desk_','HOVD_Pres_Lamp_','HOVD_Pres_Chair_','HOVD_Pres_Guest_','HOVD_Chesterfield_Chair_','HOVD_Pres_Rug','HOVD_Pres_Interpretive_','HOVD_Pres_Credenza_','HOVD_Pres_Bookcase_','HOVD_Pres_Book_Spine_','HOVD_Pres_Fireplace','HOVD_Pres_Firebox','HOVD_Pres_Embers','HOVD_Pres_Mantel_Clock'))
  else: include=include or o.name.startswith(('HOVD_Board_Table_','HOVD_Chair_','HOVD_Board_Interpretive_Credenza','HOVD_Board_Minutes_Volume_'))
  if include and abs(o.location.x)<=5.6 and abs(o.location.y-cy)<=5.7 and 3.3<=o.location.z<=8.4:o.hide_render=False
  if o.name==floorname:o.hide_render=False
 for o in s.objects:
  if o.type=='LIGHT':o.hide_render=True
 ld=bpy.data.lights.new('R4_Plan_Fill','AREA');lo=bpy.data.objects.new('R4_Plan_Fill',ld);s.collection.objects.link(lo);lo.location=center+Vector((0,0,16));ld.energy=1100;ld.shape='DISK';ld.size=12;aim(lo,center+Vector((0,0,4.6)))
 cam.location=center+Vector((0,0,17));aim(cam,center+Vector((0,0,4.5)));cam.data.ortho_scale=13
 name='presidential_office_round4.png' if tag=='Pres' else 'trustees_boardroom_round4.png';s.render.filepath=str(P/'audit/batch3_hovde'/name);bpy.ops.render.render(write_still=True);bpy.data.objects.remove(lo,do_unlink=True);bpy.data.lights.remove(ld)
print('rendered round4 exterior, portico detail, and furnished room plans from reopened canonical asset')
