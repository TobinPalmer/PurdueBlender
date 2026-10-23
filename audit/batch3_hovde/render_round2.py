import bpy
from mathutils import Vector
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');f=P/'modular/buildings/hovde_hall.blend';bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.context.scene;c=bpy.data.collections['Asset_hovde_hall']
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=64;s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.world.color=(.25,.25,.25)
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def light(n,loc,t,power,size):
 d=bpy.data.lights.new(n,'AREA');o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=loc;d.energy=power;d.shape='DISK';d.size=size;aim(o,t)
def camera(loc,t,scale):
 d=bpy.data.cameras.new('R2ReviewCamera');o=bpy.data.objects.new('R2ReviewCamera',d);s.collection.objects.link(o);o.location=loc;aim(o,t);d.type='ORTHO';d.ortho_scale=scale;s.camera=o
for o in c.all_objects:
 if o:o.hide_render=False
light('R2_Key',(70,-60,75),(-9,10,8),7000,60);light('R2_Fill',(-55,-25,40),(-9,10,8),4500,55);light('R2_Rim',(10,100,50),(-9,10,8),4000,50)
camera((95,-36,36),(5,3,8),102);s.render.filepath=str(P/'audit/batch3_hovde/exterior_round2.png');bpy.ops.render.render(write_still=True)
for tag,cy in [('Pres',-25),('Board',25)]:
 for o in c.all_objects:
  if not o:continue
  o.hide_render=True
  if o.name.startswith(f'HOVD_{tag}_'):o.hide_render=False
  if o.name.startswith('HOVD_Root') or o.name in ['HOVD_Pres_Floor','HOVD_Board_Floor']:o.hide_render=False
  if o.name.endswith('_Room_Wall_Front_L') or o.name.endswith('_Room_Wall_Front_R') or o.name.endswith('_Room_Door_Header') or o.name.endswith('_Room_Door_Leaf') or o.name.endswith('_Ceiling'):o.hide_render=True
 for o in s.objects:
  if o.type=='LIGHT' and o.name.startswith(f'HOVD_{tag}'):
   o.hide_render=False;o.data.energy=1300
 loc=(33,cy,14);target=(0,cy,6.2);camera(loc,target,24)
 name='presidential_office_round2.png' if tag=='Pres' else 'trustees_boardroom_round2.png';s.render.filepath=str(P/'audit/batch3_hovde'/name);bpy.ops.render.render(write_still=True)
print('Saved render set from reopened Hovde file')
