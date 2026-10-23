import bpy
from mathutils import Vector
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');f=P/'modular/buildings/hovde_hall.blend';bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.context.scene;c=bpy.data.collections['Asset_hovde_hall'];s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=64;s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.world.color=(.3,.3,.3)
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def camera(loc,t,scale):
 d=bpy.data.cameras.new('R2ReviewCamera');o=bpy.data.objects.new('R2ReviewCamera',d);s.collection.objects.link(o);o.location=loc;aim(o,t);d.type='ORTHO';d.ortho_scale=scale;s.camera=o
# close-up front portico/facade view with actual world center from the floor feature
for o in c.all_objects:
 if o:o.hide_render=False
floor=bpy.data.objects['HOVD_Pres_Floor']; center=floor.matrix_world.translation.copy(); direction=bpy.data.objects['HOVD_Root'].matrix_world.to_3x3() @ Vector((1,0,0));direction.normalize()
# Lights follow the modeled asset world position
for n,loc,power,size in [('R2_Key',(30,-20,40),5000,40),('R2_Fill',(-40,20,22),3000,35),('R2_Rim',(0,55,30),2500,35)]:
 d=bpy.data.lights.new(n,'AREA');o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=loc;d.energy=power;d.shape='DISK';d.size=size;aim(o,center+Vector((0,20,6)))
# entrance lies at local X+12.3, local Y~0
portico=bpy.data.objects['HOVD_Portico_Pediment_Base'].matrix_world.translation.copy()
camera(portico+direction*65+Vector((0,0,24)),portico+Vector((0,0,1)),46);s.render.filepath=str(P/'audit/batch3_hovde/exterior_round2.png');bpy.ops.render.render(write_still=True)
for tag,roomfloor in [('Pres','HOVD_Pres_Floor'),('Board','HOVD_Board_Floor')]:
 floor=bpy.data.objects[roomfloor];center=floor.matrix_world.translation.copy();
 for o in c.all_objects:
  if not o:continue
  o.hide_render=True
  if o.name.startswith(f'HOVD_{tag}_'):o.hide_render=False
  if o.name==roomfloor:o.hide_render=False
  if o.name.startswith(f'HOVD_{tag}_Room_Wall_E') or o.name.endswith('_Room_Wall_Front_L') or o.name.endswith('_Room_Wall_Front_R') or o.name.endswith('_Room_Door_Header') or o.name.endswith('_Room_Door_Leaf') or o.name.endswith('_Ceiling'):o.hide_render=True
 for o in s.objects:
  if o.type=='LIGHT' and o.name.startswith(f'HOVD_{tag}'):
   o.hide_render=False;o.data.energy=1600
 d=bpy.data.objects['HOVD_Root'].matrix_world.to_3x3() @ Vector((1,0,0));d.normalize();camloc=center+d*27+Vector((0,0,12));camera(camloc,center+Vector((0,0,1.7)),16)
 name='presidential_office_round2.png' if tag=='Pres' else 'trustees_boardroom_round2.png';s.render.filepath=str(P/'audit/batch3_hovde'/name);bpy.ops.render.render(write_still=True)
print('rendered with world-space target from saved model')
