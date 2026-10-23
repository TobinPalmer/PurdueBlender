import bpy
from mathutils import Vector
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');bpy.ops.wm.open_mainfile(filepath=str(P/'modular/buildings/hovde_hall.blend'));s=bpy.context.scene;c=bpy.data.collections['Asset_hovde_hall'];s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=80;s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.45
root=bpy.data.objects['HOVD_Root'];port=bpy.data.objects['HOVD_Portico_Entablature'].matrix_world.translation.copy();target=port+Vector((0,0,-1.1));side=(root.matrix_world.to_3x3()@Vector((1,0,0))).normalized();along=(root.matrix_world.to_3x3()@Vector((0,1,0))).normalized()
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def addlight(name,loc,t,power,size):
 d=bpy.data.lights.new(name,'AREA');o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;d.energy=power;d.shape='DISK';d.size=size;aim(o,t)
def newcam(name,loc,t,scale):
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;aim(o,t);d.type='ORTHO';d.ortho_scale=scale;s.camera=o;return o
addlight('R4B_Key',target+side*42+along*20+Vector((0,0,50)),target,2400,48);addlight('R4B_Fill',target-side*35-along*8+Vector((0,0,28)),target,1800,48);addlight('R4B_Rim',target+along*55+Vector((0,0,38)),target,1200,44)
cam=newcam('R4B_Wide',target+side*72+along*20+Vector((0,0,25)),target,96);s.render.filepath=str(P/'audit/batch3_hovde/exterior_round4.png');bpy.ops.render.render(write_still=True)
# Human-height three-quarter detail view focused on column shafts and the opening between them.
target=port+Vector((0,0,-5.0));cam.location=target+side*30+along*11+Vector((0,0,8));aim(cam,target);cam.data.ortho_scale=23;s.render.filepath=str(P/'audit/batch3_hovde/portico_detail_round4.png');bpy.ops.render.render(write_still=True)
# Reopen-style interior review: isolate room elements, use the previously validated oblique camera setup.
for tag,floorname in [('Pres','HOVD_Pres_Floor'),('Board','HOVD_Board_Floor')]:
 floor=bpy.data.objects[floorname];center=floor.matrix_world.translation.copy();cy=-25 if tag=='Pres' else 25
 for o in c.all_objects:
  if not o:continue
  o.hide_render=True
  include=o.name==floorname or o.name.startswith(f'HOVD_{tag}_') or (tag=='Board' and o.name.startswith('HOVD_Chair_')) or (tag=='Pres' and o.name.startswith('HOVD_Chesterfield_Chair_'))
  if include and abs(o.location.x)<=5.2 and abs(o.location.y-cy)<=5.6 and 3.3<=o.location.z<=8.4:o.hide_render=False
  if o.name==floorname:o.hide_render=False
  if 'Room_Wall' in o.name or 'Room_Door' in o.name or o.name.endswith('_Ceiling'):o.hide_render=True
 for o in s.objects:
  if o.type=='LIGHT':o.hide_render=True
 ld=bpy.data.lights.new('R4B_InteriorFill','AREA');lo=bpy.data.objects.new('R4B_InteriorFill',ld);s.collection.objects.link(lo);lo.location=center+Vector((0,0,10));ld.energy=1400;ld.shape='DISK';ld.size=9;aim(lo,center+Vector((0,0,1.5)))
 direction=root.matrix_world.to_3x3()@Vector((1,0,0));direction.normalize();cam.location=center+direction*16+Vector((0,-4,10));aim(cam,center+Vector((0,0,1.5)));cam.data.ortho_scale=13
 name='presidential_office_round4.png' if tag=='Pres' else 'trustees_boardroom_round4.png';s.render.filepath=str(P/'audit/batch3_hovde'/name);bpy.ops.render.render(write_still=True);bpy.data.objects.remove(lo,do_unlink=True);bpy.data.lights.remove(ld)
print('rendered current round4 saved asset set')
