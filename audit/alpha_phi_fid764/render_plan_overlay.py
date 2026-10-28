import json, os, math
from PIL import Image, ImageDraw, ImageFont

HERE=os.path.dirname(__file__)
data=json.load(open(os.path.join(HERE,'plan_comparison.json'),encoding='utf8'))
W,H=1100,880; margin=(145,95,95,110)
left,top,right,bottom=margin; plot_w=W-left-right; plot_h=H-top-bottom
(xmin,xmax),(ymin,ymax)=data['bounds_xy_m']; pad=2.6
xmin-=pad; xmax+=pad; ymin-=pad; ymax+=pad
scale=min(plot_w/(xmax-xmin),plot_h/(ymax-ymin))
used_w=(xmax-xmin)*scale; used_h=(ymax-ymin)*scale
ox=left+(plot_w-used_w)/2; oy=top+(plot_h-used_h)/2
def pix(p): return (ox+(p[0]-xmin)*scale, oy+(ymax-p[1])*scale)
img=Image.new('RGB',(W,H),'#f5f4ef'); d=ImageDraw.Draw(img)
d.rounded_rectangle((18,18,W-18,H-18),radius=12,fill='#fffefa',outline='#d6d2c6',width=2)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22); small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16); tiny=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
d.text((46,38),'Alpha Phi (FID 764) — source ring vs. wall base',font=font,fill='#20252a')
d.text((46,69),'Same local projection; source outline dashed blue, saved mesh base solid red',font=small,fill='#4b535b')
src=data['source_ring_xy_m']; model=data['model_wall_segments_xy_m']
# Source ring shown first so it remains visible beneath the coincident wall outline.
for i,a in enumerate(src):
    b=src[(i+1)%len(src)]; p1=pix(a); p2=pix(b); dx=p2[0]-p1[0]; dy=p2[1]-p1[1]; n=math.hypot(dx,dy)
    if n==0: continue
    pieces=max(1,int(n/11))
    for j in range(0,pieces,2):
        q0=j/pieces; q1=min((j+1)/pieces,1)
        d.line((p1[0]+dx*q0,p1[1]+dy*q0,p1[0]+dx*q1,p1[1]+dy*q1),fill='#2e73a8',width=6)
for seg in model:
    p1,p2=map(pix,seg); d.line((p1,p2),fill='#c54435',width=2)
for i,p in enumerate(src):
    q=pix(p); d.ellipse((q[0]-3,q[1]-3,q[0]+3,q[1]+3),fill='#2e73a8')
# North arrow and nominal scale bar.
ax,ay=W-94,top+38; d.line((ax,ay+56,ax,ay),fill='#20252a',width=3); d.polygon([(ax,ay-4),(ax-8,ay+11),(ax+8,ay+11)],fill='#20252a'); d.text((ax-9,ay-29),'N',font=small,fill='#20252a')
bar=10*scale; bx,by=left+10,H-bottom+45; d.line((bx,by,bx+bar,by),fill='#20252a',width=4); d.line((bx,by-6,bx,by+6),fill='#20252a',width=2); d.line((bx+bar,by-6,bx+bar,by+6),fill='#20252a',width=2); d.text((bx+bar+8,by-12),'10 m',font=tiny,fill='#20252a')
# Legend and checked metrics.
ly=H-74; d.line((W-510,ly+9,W-458,ly+9),fill='#2e73a8',width=6); d.text((W-450,ly-2),'official FID 764 ring',font=tiny,fill='#30363b')
d.line((W-260,ly+9,W-208,ly+9),fill='#c54435',width=3); d.text((W-198,ly-2),'saved mesh wall base',font=tiny,fill='#30363b')
txt=f"Plan bounds: {data['axis_aligned_dimensions_m'][0]:.2f} × {data['axis_aligned_dimensions_m'][1]:.2f} m   |   max boundary vertex error: {data['source_vs_model_max_boundary_vertex_error_m']:.4f} m"
d.text((46,H-40),txt,font=tiny,fill='#4b535b')
img.save(os.path.join(HERE,'plan_overlay.png'))
