import bpy,math,pathlib,json
from mathutils import Vector,Euler
P=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');A=P/'audit/batch3_elliott';src=P/'modular/buildings/elliott_hall_of_music.blend';bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=48;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0.0
ring=json.load(open(A/'polygon.json')); area=.5*sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)));best=(1e9,None)
for i,a in enumerate(ring):
 b=ring[(i+1)%len(ring)];dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy;u=max(0,min(1,((44.075-a[0])*dx+(9.162-a[1])*dy)/den));pp=(a[0]+u*dx,a[1]+u*dy);dist=math.dist(pp,(44.075,9.162))
 if dist<best[0]:
  L=math.hypot(dx,dy);t=(dx/L,dy/L);n=(t[1],-t[0]) if area>0 else (-t[1],t[0]);best=(dist,(pp,t,n))
p,t,n=best[1]
def render(name,loc,target,scale,allow=None,rot=None,res=(1600,1050)):
 old=[]
 for o in s.objects:
  hide=(allow is not None and o.name not in allow)
  if o.name.startswith('TEMP_R9_') and o.type not in {'CAMERA','LIGHT'}:hide=True
  if o.type=='LIGHT' and o.name.startswith('TEMP_R9_') and allow is not None and o.name not in allow:hide=True
  if hide:old.append((o,o.hide_render));o.hide_render=True
 d=bpy.data.cameras.new('TEMP_R9_CAM_'+name);d.type='ORTHO';d.ortho_scale=scale;cam=bpy.data.objects.new('TEMP_R9_CAM_'+name,d);s.collection.objects.link(cam);cam.location=loc;q=(Vector(target)-cam.location).to_track_quat('-Z','Y')
 if rot is not None:q=q@Euler((0,0,rot),'XYZ').to_quaternion()
 cam.rotation_euler=q.to_euler();s.camera=cam;s.render.resolution_x,s.render.resolution_y=res;s.render.filepath=str(A/(name+'.png'));bpy.ops.render.render(write_still=True)
 for o,v in old:o.hide_render=v
 bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(d)
# Temporary soft fill sources
for nm,energy,size,loc,target in [('TEMP_R9_Entry_Key',3000,13,(p[0]+n[0]*13,p[1]+n[1]*13,13),(p[0],p[1],5.5)),('TEMP_R9_Auditorium_Key',40000,40,(0,0,29),(0,0,7))]:
 d=bpy.data.lights.new(nm,'AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new(nm,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
# fixed sky fill
if s.world and s.world.use_nodes:
 bg=s.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(0.55,0.58,0.62,1);bg.inputs['Strength'].default_value=1.2
entry_allow={o.name for o in s.objects if not (o.name.startswith('ELLT_R4_Hovde_') or 'Hovde_Link' in o.name)}
render('entry_portal_round9',(p[0]+n[0]*15,p[1]+n[1]*15,10),(p[0]+n[0]*.15,p[1]+n[1]*.15,5.8),12.5,entry_allow)
interior={o.name for o in s.objects if o.name.startswith('ELLT_B3_') and any(k in o.name.lower() for k in ('seat','stage','curtain','balcony','rail','stair','carpet','plaster','frame','aisle','wall','ceiling')) and 'ceiling' not in o.name.lower()}
interior.add('TEMP_R9_Auditorium_Key')
render('interior_audience_round9',(-18,-26,17),(3,11,6.8),58,interior)
render('interior_plan_round9',(0,0,100),(0,0,6),84,interior,rot=math.radians(50.64),res=(1600,1250))
