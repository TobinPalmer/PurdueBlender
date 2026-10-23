import bpy
from mathutils import Vector
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');bpy.ops.wm.open_mainfile(filepath=str(P/'modular/buildings/hovde_hall.blend'));s=bpy.context.scene;c=bpy.data.collections['Asset_hovde_hall'];s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=64;s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.1
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
for tag,floorname in [('Pres','HOVD_Pres_Floor'),('Board','HOVD_Board_Floor')]:
 floor=bpy.data.objects[floorname];center=floor.matrix_world.translation.copy();cy=-25 if tag=='Pres' else 25
 for o in c.all_objects:
  if not o:continue
  o.hide_render=True
  include=o.name==floorname or o.name.startswith(f'HOVD_{tag}_') or (tag=='Board' and o.name.startswith('HOVD_Chair_')) or (tag=='Pres' and o.name.startswith('HOVD_Chesterfield_Chair_'))
  if include and abs(o.location.x)<=5.4 and abs(o.location.y-cy)<=5.4 and 3.3<=o.location.z<=8.4:o.hide_render=False
  if o.name==floorname:o.hide_render=False
  if 'Room_Wall' in o.name or 'Room_Door' in o.name or o.name.endswith('_Ceiling'):o.hide_render=True
 for o in s.objects:
  if o.type=='LIGHT':o.hide_render=True
 ld=bpy.data.lights.new('InteriorReviewFill','AREA');lo=bpy.data.objects.new('InteriorReviewFill',ld);s.collection.objects.link(lo);lo.location=center+Vector((0,0,10));ld.energy=1200;ld.shape='DISK';ld.size=9;aim(lo,center+Vector((0,0,1.5)))
 direction=bpy.data.objects['HOVD_Root'].matrix_world.to_3x3() @ Vector((1,0,0));direction.normalize();camloc=center+direction*16+Vector((0,-4,10));d=bpy.data.cameras.new('HovdeInteriorEvidence');cam=bpy.data.objects.new('HovdeInteriorEvidence',d);s.collection.objects.link(cam);cam.location=camloc;aim(cam,center+Vector((0,0,1.5)));d.type='ORTHO';d.ortho_scale=11;s.camera=cam
 filename='presidential_office_round3.png' if tag=='Pres' else 'trustees_boardroom_round3.png';s.render.filepath=str(P/'audit/batch3_hovde'/filename);bpy.ops.render.render(write_still=True);bpy.data.objects.remove(lo,do_unlink=True);bpy.data.lights.remove(ld)
print('rendered current saved-file room review images')
