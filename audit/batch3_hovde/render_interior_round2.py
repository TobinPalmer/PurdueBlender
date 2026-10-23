import bpy
from mathutils import Vector
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');f=P/'modular/buildings/hovde_hall.blend';bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.context.scene;c=bpy.data.collections['Asset_hovde_hall'];s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=64;s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.5
for tag,floorname in [('Pres','HOVD_Pres_Floor'),('Board','HOVD_Board_Floor')]:
 floor=bpy.data.objects[floorname];center=floor.matrix_world.translation.copy();cy=-25 if tag=='Pres' else 25
 for o in c.all_objects:
  if not o:continue
  o.hide_render=True
  include=o.name==floorname or o.name.startswith(f'HOVD_{tag}_') or (tag=='Board' and o.name.startswith('HOVD_Chair_')) or (tag=='Pres' and o.name.startswith('HOVD_Chesterfield_Chair_'))
  if include and abs(o.location.x)<=7.2 and abs(o.location.y-cy)<=7.4 and 3.3<=o.location.z<=8.4:o.hide_render=False
  if o.name==floorname:o.hide_render=False
  if 'Room_Wall' in o.name or 'Room_Door' in o.name or o.name.endswith('_Ceiling'):o.hide_render=True
 for o in s.objects:
  if o.type=='LIGHT':o.hide_render=True
 ld=bpy.data.lights.new('InteriorEvidenceFill','AREA');lo=bpy.data.objects.new('InteriorEvidenceFill',ld);s.collection.objects.link(lo);lo.location=center+Vector((1,-3,10));ld.energy=1400;ld.shape='DISK';ld.size=10;lo.rotation_euler=(Vector(center+Vector((0,0,2)))-lo.location).to_track_quat('-Z','Y').to_euler()
 d=bpy.data.objects['HOVD_Root'].matrix_world.to_3x3() @ Vector((1,0,0));d.normalize();loc=center+d*18+Vector((0,-5,12));camdata=bpy.data.cameras.new('InteriorSection');cam=bpy.data.objects.new('InteriorSection',camdata);s.collection.objects.link(cam);cam.location=loc;cam.rotation_euler=(center+Vector((0,0,2))-loc).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=14;s.camera=cam
 name='presidential_office_round2.png' if tag=='Pres' else 'trustees_boardroom_round2.png';s.render.filepath=str(P/'audit/batch3_hovde'/name);bpy.ops.render.render(write_still=True);bpy.data.objects.remove(lo,do_unlink=True);bpy.data.lights.remove(ld)
print('rendered clean room-only section evidence')
