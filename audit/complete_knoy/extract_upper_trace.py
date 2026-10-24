import bpy,numpy as np,math,json,os
from mathutils import Vector
root=r'C:\Users\Tobin\Documents\Blender\PurdueMap'
imgpath=root+r'\audit\complete_knoy\knoy_typical_plan_crop.png'
gisp=root+r'\audit\batch4_knoy\gis_vertices_local.json'
out=root+r'\audit\complete_knoy\upper_plan_wall_trace.json'
im=bpy.data.images.load(imgpath,check_existing=False);w,h=im.size
pix=np.array(im.pixels[:],dtype=np.float32).reshape((h,w,4))[::-1].copy();gray=pix[:,:,:3].mean(axis=2)
rgb=pix[:,:,:3]; dark=(gray<.8)&((rgb.max(axis=2)-rgb.min(axis=2))<.16)
y,x=np.where(dark); sel=(x>=95)&(x<=550)&(y>=130)&(y<=1280);x=x[sel];y=y[sel]
# Hough-like run extraction for the dominant plan directions.
cands=[]
for deg in [0,45,90,135]:
 th=math.radians(deg);dx=math.cos(th);dy=math.sin(th)
 rho=np.rint(-x*dy+y*dx).astype(int);t=np.rint(x*dx+y*dy).astype(int)
 for r in np.unique(rho):
  ts=np.sort(t[rho==r])
  if not len(ts):continue
  vals=np.zeros(int(ts[-1]-ts[0]+1),dtype=np.bool_);vals[ts-ts[0]]=True
  idx=np.where(vals)[0]
  if not len(idx):continue
  runs=[];st=pr=idx[0]
  for z in idx[1:]:
   if z-pr>3:
    runs.append((st,pr));st=z
   pr=z
  runs.append((st,pr))
  for st,en in runs:
   L=en-st
   if L<16:continue
   t0=st+ts[0];t1=en+ts[0]
   p0=(dx*t0-dy*r,dy*t0+dx*r);p1=(dx*t1-dy*r,dy*t1+dx*r)
   if min(p0[0],p1[0])<95 or max(p0[0],p1[0])>550 or min(p0[1],p1[1])<130 or max(p0[1],p1[1])>1280:continue
   cands.append([deg,int(r),float(t0),float(t1),p0,p1,L])
# Cluster parallel stroke/anti-alias candidates into a single centerline run.
merged=[]
for deg in [0,45,90,135]:
 group=sorted([c for c in cands if c[0]==deg],key=lambda z:(z[1],z[2]))
 clusters=[]
 for c in group:
  best=None
  for cl in clusters[-10:]:
   if abs(cl['rho']-c[1])<=2 and c[2]<=cl['t1']+4 and c[3]>=cl['t0']-4:
    best=cl;break
  if best is None:clusters.append({'rho':c[1],'t0':c[2],'t1':c[3]})
  else:
   best['rho']=(best['rho']+c[1])/2;best['t0']=min(best['t0'],c[2]);best['t1']=max(best['t1'],c[3])
 th=math.radians(deg);dx=math.cos(th);dy=math.sin(th)
 for cl in clusters:
  if cl['t1']-cl['t0']<14:continue
  rr=cl['rho'];t0=cl['t0'];t1=cl['t1']
  merged.append([deg,rr,t0,t1,(dx*t0-dy*rr,dy*t0+dx*rr),(dx*t1-dy*rr,dy*t1+dx*rr)])
# Pixel-to-local-world affine fit from three visibly corresponding outline controls.
controls=[(382,139,5.230,46.581),(107,1253,-15.416,-46.581),(507,1253,16.928,-45.998)]
A=np.array([[u,v,1] for u,v,xx,yy in controls],dtype=float)
mx=np.linalg.solve(A,np.array([xx for u,v,xx,yy in controls]));my=np.linalg.solve(A,np.array([yy for u,v,xx,yy in controls]))
def xy(p):return [float(mx[0]*p[0]+mx[1]*p[1]+mx[2]),float(my[0]*p[0]+my[1]*p[1]+my[2])]
poly=np.array(json.load(open(gisp,encoding='utf-8')),dtype=float)
def dseg(p,a,b):
 v=b-a;den=max(1e-12,float(v@v));q=np.clip(float((p-a)@v)/den,0,1);return float(np.linalg.norm(p-(a+q*v)))
def dpoly(p):return min(dseg(p,poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly)))
# Exclude exterior-wall strokes (GIS registration) and plan symbols known to be stairs.
stair_boxes=[(360,165,410,225),(100,690,190,785),(435,1195,515,1270)]
result=[]
for deg,r,t0,t1,p0,p1 in merged:
 Lpx=t1-t0; p0=list(p0);p1=list(p1);mid=((p0[0]+p1[0])/2,(p0[1]+p1[1])/2);world0=xy(p0);world1=xy(p1);midw=np.array(xy(mid))
 if dpoly(midw)<1.2:continue
 if any(x0<=mid[0]<=x1 and y0<=mid[1]<=y1 for x0,y0,x1,y1 in stair_boxes):continue
 length=float(np.linalg.norm(np.array(world1)-np.array(world0)))
 if length<1.25:continue
 result.append({'source_pixels':[p0,p1],'local_xy_m':[world0,world1],'angle_deg':deg,'length_px':round(Lpx,2),'length_m':round(length,3),'boundary_clearance_m':round(dpoly(midw),3)})
report={'source_image':'audit/complete_knoy/knoy_typical_plan_crop.png','pdf_page':24,'source_date':'2018-05-31 planning study','registration':'3 manually selected outline controls to official Purdue GIS; hand-affine fit, approximately +/-1m, not survey','pixel_to_local_xy_affine':{'x':[float(z) for z in mx],'y':[float(z) for z in my]},'threshold':'luminance <0.8 and chroma <0.16; dominant straight directions 0/45/90/135 degrees; centerline runs >=1.25m; short joins <=3 pixels','candidate_run_count':len(cands),'merged_run_count':len(merged),'accepted_interior_segments':len(result),'exclusions':'near-GIS-boundary traces under 1.2m, manually masked stair-core boxes, traces under 1.25m','segments':result}
with open(out,'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
print('run counts',len(cands),len(merged),len(result));print('affine',mx,my);print('length range',min(s['length_m'] for s in result),max(s['length_m'] for s in result))



