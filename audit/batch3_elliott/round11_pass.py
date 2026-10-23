import bpy, pathlib, json, math
from mathutils import Vector
P=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); A=P/'audit/batch3_elliott'; src=P/'modular/buildings/elliott_hall_of_music.blend'
bpy.ops.wm.open_mainfile(filepath=str(src)); s=bpy.context.scene; c=bpy.data.collections['Asset_elliott_hall_of_music']
# Purdue Convocations' current venue-photo description identifies gray cushioned seats.
# Apply restrained neutral-gray fabric and keep the existing procedural surface texture.
m=bpy.data.materials['ELLT_B3_Theatre_Seat_Brown_Fabric']; m.name='ELLT_B3_Theatre_Seat_Gray_Fabric_Estimated'; m.diffuse_color=(.19,.20,.21,1)
for n in m.node_tree.nodes:
 if n.type=='VALTORGB':
  es=n.color_ramp.elements
  es[0].color=(.115,.126,.14,1); es[1].color=(.205,.22,.24,1)
 if n.type=='TEX_NOISE':
  n.inputs['Scale'].default_value=95; n.inputs['Detail'].default_value=2.5
 if n.type=='BUMP':
  n.inputs['Strength'].default_value=.09; n.inputs['Distance'].default_value=.00045
m['source_note']='Purdue Convocations current venue-photo description identifies gray cushioned seats; precise upholstery color/texture remains an approximation.'
for o in c.objects:
 if o.type=='MESH' and 'seat' in o.name.lower(): o['round11_finish']='Subtle neutral-gray fabric treatment based on official Purdue venue-photo description; individual seat design and upholstery detail remain schematic.'
# Preserve landing deferral and footprint-related asset data.
land=bpy.data.objects.get('ELLT_R8_Elliott_Side_Interface_Landing_Estimated')
if land: land['interface_status']='Elliott-only provisional landing. Hovde portal/connector unverified; do not infer continuous route from GIS footprint contact.'
bpy.ops.wm.save_as_mainfile(filepath=str(src))
# Render temporary scene-only evidence; temporary cameras/lights are removed before process exit.
s.render.engine='BLENDER_EEVEE'; s.eevee.taa_render_samples=64; s.view_settings.view_transform='AgX'; s.view_settings.look='AgX - Medium High Contrast'; s.view_settings.exposure=.25
s.render.resolution_x=1600;s.render.resolution_y=1050;s.render.resolution_percentage=100
# whole mass context, low oblique to show tiled roof, flytower, round apse and entries
ld=bpy.data.lights.new('TEMP_R11_Sun','SUN');ld.energy=2.1;lo=bpy.data.objects.new('TEMP_R11_Sun',ld);s.collection.objects.link(lo);lo.rotation_euler=(.45,.25,.7)
def render(name,loc,target,scale,allowed=None):
 hidden=[]
 for o in s.objects:
  h=allowed is not None and o.name not in allowed
  if h:hidden.append((o,o.hide_render));o.hide_render=True
 cd=bpy.data.cameras.new('TEMP_R11_Cam_'+name);cd.type='ORTHO';cd.ortho_scale=scale;cam=bpy.data.objects.new('TEMP_R11_Cam_'+name,cd);s.collection.objects.link(cam);cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam;s.render.filepath=str(A/(name+'.png'));bpy.ops.render.render(write_still=True)
 for o,v in hidden:o.hide_render=v
 bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(cd)
render('exterior_round11',(115,-135,90),(0,0,12),138)
interior={o.name for o in s.objects if o.name.startswith('ELLT_B3_') and any(k in o.name.lower() for k in ('seat','stage','curtain','balcony','rail','stair','carpet','plaster','frame','aisle','wall'))}
ld2=bpy.data.lights.new('TEMP_R11_Interior_Fill','AREA');ld2.energy=38000;ld2.shape='DISK';ld2.size=38;li=bpy.data.objects.new('TEMP_R11_Interior_Fill',ld2);s.collection.objects.link(li);li.location=(0,0,28);li.rotation_euler=(Vector((0,0,6))-li.location).to_track_quat('-Z','Y').to_euler()
interior.add(li.name)
render('interior_from_stage_round11',(22,29,13),(-8,-8,6.5),66,interior)
# cleanup render-only objects (asset save is already complete)
for o in list(s.objects):
 if o.name.startswith('TEMP_R11_'):
  d=o.data;bpy.data.objects.remove(o,do_unlink=True)
  if d and d.users==0:
   (bpy.data.cameras if d.type=='CAMERA' else bpy.data.lights).remove(d)
print(json.dumps({'saved':str(src),'mesh_count':sum(o.type=='MESH' for o in c.objects),'seat_material':m.name,'renders':['exterior_round11.png','interior_from_stage_round11.png']}))
