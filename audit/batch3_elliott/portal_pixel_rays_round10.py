import bpy,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend');s=bpy.context.scene;ring=__import__('json').load(open(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_elliott/polygon.json'));area=.5*sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)));best=(1e9,None)
for i,a in enumerate(ring):
 b=ring[(i+1)%len(ring)];dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy;u=max(0,min(1,((44.075-a[0])*dx+(9.162-a[1])*dy)/den));q=(a[0]+u*dx,a[1]+u*dy);dist=math.dist(q,(44.075,9.162))
 if dist<best[0]:
  L=math.hypot(dx,dy);t=(dx/L,dy/L);n=(t[1],-t[0]) if area>0 else (-t[1],t[0]);best=(dist,(q,t,n))
p,t,n=best[1];loc=Vector((p[0]+n[0]*18,p[1]+n[1]*18,11));target=Vector((p[0]+n[0]*.2,p[1]+n[1]*.2,5.8));quat=(target-loc).to_track_quat('-Z','Y');right=quat@Vector((1,0,0));up=quat@Vector((0,1,0));direction=quat@Vector((0,0,-1));
for px,py in [(772,583),(770,565),(780,585),(800,580)]:
 x=(px/1600-.5)*17.5;y=(.5-py/1050)*(17.5*1050/1600);origin=loc+right*x+up*y;dg=bpy.context.evaluated_depsgraph_get();ok,hit,norm,face,ob,mat=s.ray_cast(dg,origin,direction); print((px,py),tuple(round(a,2) for a in hit),ob.name if ob else None)
