import bpy, math, pathlib, json
from mathutils import Vector
P=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); A=P/'audit/batch3_elliott'; src=P/'modular/buildings/elliott_hall_of_music.blend'
bpy.ops.wm.open_mainfile(filepath=str(src)); s=bpy.context.scene; coll=bpy.data.collections['Asset_elliott_hall_of_music']
# Reduce broad softbox reflection that made an opaque tinted door look like an overlapping pale panel.
glass=bpy.data.materials['ELLT_R8_Door_Glass_Estimated']; bsdf=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); bsdf.inputs['Base Color'].default_value=(0.045,0.115,0.145,1); bsdf.inputs['Roughness'].default_value=.68; bsdf.inputs['Specular IOR Level'].default_value=.12; bsdf.inputs['Metallic'].default_value=0; bsdf.inputs['Transmission Weight'].default_value=0; glass.diffuse_color=(.045,.115,.145,1)
for name in ('ELLT_R8_Upper_Portal_DoorLeaf_L_Estimated','ELLT_R8_Upper_Portal_DoorLeaf_R_Estimated'):
 o=bpy.data.objects[name];o['round10_change']='Door material roughness/specular reduced to avoid bright area-light reflection reading as an overlapping obstruction; surface remains a simplified estimated tinted glazing.'
# Preserve the landing deferral as metadata on the Elliott-only object.
landing=bpy.data.objects.get('ELLT_R8_Elliott_Side_Interface_Landing_Estimated')
if landing: landing['interface_status']='Elliott-only provisional landing. Hovde portal/connector unverified; do not infer continuous route from GIS footprint contact.'
bpy.ops.wm.save_as_mainfile(filepath=str(src))
# Render passes are temporary and are not saved into the asset.
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=48;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0
ring=json.load(open(A/'polygon.json'));area=.5*sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)));best=(1e9,None)
for i,a in enumerate(ring):
 b=ring[(i+1)%len(ring)];dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy;u=max(0,min(1,((44.075-a[0])*dx+(9.162-a[1])*dy)/den));pp=(a[0]+u*dx,a[1]+u*dy);dist=math.dist(pp,(44.075,9.162))
 if dist<best[0]:
  L=math.hypot(dx,dy);t=(dx/L,dy/L);n=(t[1],-t[0]) if area>0 else (-t[1],t[0]);best=(dist,(pp,t,n))
p,t,n=best[1]
# Temporary area lights for the evidence views.
for nm,energy,size,loc,target in [('TEMP_R10_Entry_Fill',1200,9,(p[0]+n[0]*14,p[1]+n[1]*14,12),(p[0],p[1],5.8)),('TEMP_R10_Interior_Fill',32000,35,(0,0,28),(0,0,7))]:
 d=bpy.data.lights.new(nm,'AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new(nm,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
if s.world and s.world.use_nodes:
 bg=s.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.5,.53,.58,1);bg.inputs['Strength'].default_value=.85

def render(name,loc,target,scale,allowed,res=(1600,1050)):
 hidden=[]
 for o in s.objects:
  h=(allowed is not None and o.name not in allowed)
  if h:hidden.append((o,o.hide_render));o.hide_render=True
 d=bpy.data.cameras.new('TEMP_R10_CAM_'+name);d.type='ORTHO';d.ortho_scale=scale;cam=bpy.data.objects.new('TEMP_R10_CAM_'+name,d);s.collection.objects.link(cam);cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam;s.render.resolution_x,s.render.resolution_y=res;s.render.filepath=str(A/(name+'.png'));bpy.ops.render.render(write_still=True)
 for o,v in hidden:o.hide_render=v
 bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(d)
entry_allow={o.name for o in s.objects if not (o.name.startswith('ELLT_R4_Hovde_') or 'Hovde_Link' in o.name)}
entry_allow.add('TEMP_R10_Entry_Fill')
render('entry_portal_round10',(p[0]+n[0]*18,p[1]+n[1]*18,11.0),(p[0]+n[0]*.2,p[1]+n[1]*.2,5.8),17.5,entry_allow)
interior={o.name for o in s.objects if o.name.startswith('ELLT_B3_') and any(k in o.name.lower() for k in ('seat','stage','curtain','balcony','rail','stair','carpet','plaster','frame','aisle','wall','ceiling')) and 'ceiling' not in o.name.lower()};interior.add('TEMP_R10_Interior_Fill')
render('interior_from_stage_round10',(22,29,13),(-8,-8,6.5),66,interior)
# Clear temporary render objects from live data (they were never saved).
for ob in list(s.objects):
 if ob.name.startswith('TEMP_R10_'):
  data=ob.data;bpy.data.objects.remove(ob,do_unlink=True)
  if data and data.users==0:
   if data.type=='CAMERA':bpy.data.cameras.remove(data)
   else:bpy.data.lights.remove(data)
print(json.dumps({'asset_saved':str(src),'door_material':{'roughness':bsdf.inputs['Roughness'].default_value,'specular':bsdf.inputs['Specular IOR Level'].default_value},'mesh_count':sum(o.type=='MESH' for o in coll.objects),'renders':['entry_portal_round10.png','interior_from_stage_round10.png']}))
