import bpy,numpy as np,json
r='C:/Users/Tobin/Documents/Blender/PurdueMap/audit/complete_knoy'
im=bpy.data.images.load(r+'/knoy_typical_plan_crop.png',check_existing=False);w,h=im.size
a=np.array(im.pixels[:],dtype=np.float32).reshape((h,w,4))[::-1].copy()
data=json.load(open(r+'/upper_plan_wall_trace.json',encoding='utf-8'))['segments']
for s in data:
 p0,p1=s['source_pixels'];L=max(abs(p1[0]-p0[0]),abs(p1[1]-p0[1]));n=max(2,int(L*2))
 for i in range(n+1):
  t=i/n;x=round(p0[0]*(1-t)+p1[0]*t);y=round(p0[1]*(1-t)+p1[1]*t)
  if 0<=x<w and 0<=y<h:a[y,x,:3]=(0.05,0.7,0.1);a[y,x,3]=1
out=bpy.data.images.new('Upper floor wall trace overlay',width=w,height=h,alpha=True);out.pixels[:]=a.reshape(-1).tolist();out.filepath_raw=r+'/upper_plan_wall_trace_overlay.png';out.file_format='PNG';out.save();print('saved overlay',len(data))
