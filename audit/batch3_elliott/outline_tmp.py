import bpy,math
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend');o=bpy.data.objects['ELLT_Official_Footprint_Exterior_Walls'];N=len(o.data.vertices)//2;pts=[(v.co.x,v.co.y) for v in o.data.vertices[:N]]
def rdp(p,e):
 if len(p)<3:return p
 ax,ay=p[0];bx,by=p[-1];dx=bx-ax;dy=by-ay;den=dx*dx+dy*dy;best=-1;idx=0
 for i,(x,y) in enumerate(p[1:-1],1):
  t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/den)) if den else 0;d=math.hypot(x-(ax+t*dx),y-(ay+t*dy))
  if d>best:best=d;idx=i
 if best>e:return rdp(p[:idx+1],e)[:-1]+rdp(p[idx:],e)
 return [p[0],p[-1]]
far=max(range(1,N),key=lambda i:(pts[i][0]-pts[0][0])**2+(pts[i][1]-pts[0][1])**2);a=rdp(pts[:far+1],.8);b=rdp(pts[far:]+pts[:1],.8);simp=a[:-1]+b[:-1]+[pts[0]]
idxs=[min(range(N),key=lambda i:(pts[i][0]-p[0])**2+(pts[i][1]-p[1])**2) for p in simp[:-1]]
ls=[]
for k,i in enumerate(idxs):
 j=idxs[(k+1)%len(idxs)];out=[pts[i]];x=i
 while x!=j:
  x=(x+1)%N;out.append(pts[x])
  if len(out)>N+1:break
 L=sum(math.dist(x,y) for x,y in zip(out,out[1:]));ls.append((i,j,L))
print('N',N,'n Simple',len(idxs),'max',max(x[2] for x in ls),'long',sorted([round(x[2],2) for x in ls],reverse=True)[:10])
