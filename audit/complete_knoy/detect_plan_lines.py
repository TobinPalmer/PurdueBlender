import bpy,numpy as np,math
path=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\complete_knoy\knoy_typical_plan_crop.png'
out=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\complete_knoy\plan_line_candidates.png'
im=bpy.data.images.load(path,check_existing=False); w,h=im.size
a=np.array(im.pixels[:],dtype=np.float32).reshape((h,w,4)); a=a[::-1].copy(); g=a[:,:,:3].mean(axis=2)
dark=(g<.5)
y,x=np.where(dark); region=(x>=95)&(x<=550)&(y>=130)&(y<=1280); x=x[region];y=y[region]
segments=[]
for deg in [0,45,90,135]:
 th=math.radians(deg); dx=math.cos(th);dy=math.sin(th)
 rho=np.rint(-x*dy+y*dx).astype(int);t=np.rint(x*dx+y*dy).astype(int)
 for r in np.unique(rho):
  ts=np.sort(t[rho==r]);
  if not len(ts):continue
  # collapse same bins and fill small gaps
  vals=np.zeros(int(ts[-1]-ts[0]+1),dtype=np.bool_);vals[ts-ts[0]]=True
  idx=np.where(vals)[0]
  if not len(idx):continue
  groups=[];st=pr=idx[0]
  for z in idx[1:]:
   if z-pr>3:
    groups.append((st,pr));st=z
   pr=z
  groups.append((st,pr))
  for st,en in groups:
   if en-st<12:continue
   a0=(dx*(st+ts[0])-dy*r,dy*(st+ts[0])+dx*r);a1=(dx*(en+ts[0])-dy*r,dy*(en+ts[0])+dx*r)
   if min(a0[0],a1[0])<100 or max(a0[0],a1[0])>550 or min(a0[1],a1[1])<130 or max(a0[1],a1[1])>1280:continue
   segments.append((deg,a0,a1,en-st))
print('segments',len(segments))
# overlay diagnostic; detected candidate is red. Exclude near-black underlying rendering.
for deg,p0,p1,L in segments:
 n=max(2,int(L*2));
 for q in range(n+1):
  u=q/n; px=round(p0[0]*(1-u)+p1[0]*u);py=round(p0[1]*(1-u)+p1[1]*u)
  if 0<=px<w and 0<=py<h: a[py,px,:3]=(1,.05,.05);a[py,px,3]=1
im2=bpy.data.images.new('Detected plan linework',width=w,height=h,alpha=True);im2.pixels[:]=a.reshape(-1).tolist();im2.filepath_raw=out;im2.file_format='PNG';im2.save()
