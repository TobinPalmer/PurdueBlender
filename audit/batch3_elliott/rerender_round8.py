import bpy,math,pathlib
from mathutils import Vector
P=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');A=P/'audit/batch3_elliott'
bpy.ops.wm.open_mainfile(filepath=str(P/'modular/buildings/elliott_hall_of_music.blend'));s=bpy.context.scene
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1600;s.render.resolution_y=1050;s.render.resolution_percentage=100;s.eevee.taa_render_samples=32;s.view_settings.view_transform='AgX'

def render(name,loc,target,scale,allowed=None,hide_prefixes=(),hide_exact=()):
 changes=[]
 for o in s.objects:
  hide=(allowed is not None and o.name not in allowed) or any(o.name.startswith(x) for x in hide_prefixes) or o.name in hide_exact
  if hide: changes.append((o,o.hide_render));o.hide_render=True
 d=bpy.data.cameras.new('TEMP_R8_'+name);d.type='ORTHO';c=bpy.data.objects.new('TEMP_R8_'+name,d);s.collection.objects.link(c);c.location=loc;d.ortho_scale=scale;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();s.camera=c;s.render.filepath=str(A/(name+'.png'));bpy.ops.render.render(write_still=True)
 for o,v in changes:o.hide_render=v
 bpy.data.objects.remove(c,do_unlink=True);bpy.data.cameras.remove(d)

# Rebuild render-only key light (not saved).
ld=bpy.data.lights.new('TEMP_R8_Key','SUN');ld.energy=2.2;l=bpy.data.objects.new('TEMP_R8_Key',ld);s.collection.objects.link(l);l.rotation_euler=(math.radians(27),math.radians(-30),math.radians(-22))
# Correct camera to approach Elliott's facade from its modeled outward normal.
ring=__import__('json').load(open(A/'polygon.json'));area=.5*sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)));best=(1e9,None)
for i,a in enumerate(ring):
 b=ring[(i+1)%len(ring)];dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy;u=max(0,min(1,((44.075-a[0])*dx+(9.162-a[1])*dy)/den));p0=(a[0]+u*dx,a[1]+u*dy);dist=math.dist(p0,(44.075,9.162))
 if dist<best[0]:
  L=math.hypot(dx,dy);t=(dx/L,dy/L);n=(t[1],-t[0]) if area>0 else (-t[1],t[0]);best=(dist,(p0,t,n))
p,t,n=best[1];render('entry_portal_round8',(p[0]+n[0]*23,p[1]+n[1]*23,13),(p[0]+n[0]*.2,p[1]+n[1]*.2,5.8),18,hide_prefixes=('ELLT_R4_Hovde_',))
# Only auditorium objects are visible in these evidence views; this eliminates exterior legacy walls.
allowed={'ELLT_B3_seat','ELLT_B3_stage','ELLT_B3_curtain','ELLT_B3_balcony','ELLT_B3_ceiling'}
render('interior_audience_round8',(4,-29,12),(11,18,7),62,allowed=allowed,hide_exact={'ELLT_B3_ceiling'})
render('interior_plan_round8',(0,0,90),(0,0,5),78,allowed=allowed,hide_exact={'ELLT_B3_ceiling'})
