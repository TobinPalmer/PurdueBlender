import bpy
from mathutils import Vector
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');f=P/'modular/buildings/hovde_hall.blend';bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.context.scene;c=bpy.data.collections['Asset_hovde_hall'];s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=96;s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.7;s.world.color=(.12,.12,.12)
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def add_area(n,loc,t,power,size):
 d=bpy.data.lights.new(n,'AREA');o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=loc;d.energy=power;d.shape='DISK';d.size=size;aim(o,t)
def camera(loc,t,scale):
 d=bpy.data.cameras.new('Round3Camera');o=bpy.data.objects.new('Round3Camera',d);s.collection.objects.link(o);o.location=loc;aim(o,t);d.type='ORTHO';d.ortho_scale=scale;s.camera=o
for o in c.all_objects:
 if o:o.hide_render=False
center=bpy.data.objects['HOVD_Root'].matrix_world.translation.copy();target=center+Vector((0,0,8))
add_area('R3_Key',center+Vector((35,-45,55)),target,1800,35);add_area('R3_Fill',center+Vector((-50,-15,28)),target,1100,45);add_area('R3_Rim',center+Vector((15,55,35)),target,900,35)
camera(target+Vector((55,-62,40)),target,94);s.render.filepath=str(P/'audit/batch3_hovde/exterior_round3.png');bpy.ops.render.render(write_still=True)
# interior plan/cutaway: use only room-local objects within the reduced room footprint; omit near walls and ceilings for readability.
for tag,floorname in [('Pres','HOVD_Pres_Floor'),('Board','HOVD_Board_Floor')]:
 floor=bpy.data.objects[floorname];center=floor.matrix_world.translation.copy();cy=-25 if tag=='Pres' else 25
 for o in c.all_objects:
  if not o:continue
  o.hide_render=True
  include=o.name==floorname or o.name.startswith(f'HOVD_{tag}_') or (tag=='Board' and o.name.startswith('HOVD_Chair_')) or (tag=='Pres' and o.name.startswith('HOVD_Chesterfield_Chair_'))
  if include and abs(o.location.x)<=5.2 and abs(o.location.y-cy)<=5.2 and 3.3<=o.location.z<=8.4:o.hide_render=False
  if o.name==floorname:o.hide_render=False
  if 'Room_Wall' in o.name or 'Room_Door' in o.name or o.name.endswith('_Ceiling'):o.hide_render=True
 for o in s.objects:
  if o.type=='LIGHT':o.hide_render=True
 ld=bpy.data.lights.new('InteriorReviewFill','AREA');lo=bpy.data.objects.new('InteriorReviewFill',ld);s.collection.objects.link(lo);lo.location=center+Vector((0,0,10));ld.energy=500;ld.shape='DISK';ld.size=9;aim(lo,center+Vector((0,0,1.5)))
 direction=bpy.data.objects['HOVD_Root'].matrix_world.to_3x3() @ Vector((1,0,0));direction.normalize();camloc=center+direction*16+Vector((0,-4,10));camera(camloc,center+Vector((0,0,1.5)),11)
 filename='presidential_office_round3.png' if tag=='Pres' else 'trustees_boardroom_round3.png';s.render.filepath=str(P/'audit/batch3_hovde'/filename);bpy.ops.render.render(write_still=True);bpy.data.objects.remove(lo,do_unlink=True);bpy.data.lights.remove(ld)
print('rendered saved-file round3 review set')
