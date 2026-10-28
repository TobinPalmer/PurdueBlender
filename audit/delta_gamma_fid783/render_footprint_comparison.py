import json, os, math
from PIL import Image, ImageDraw, ImageFont
HERE=os.path.dirname(__file__)
data=json.load(open(os.path.join(HERE,'legacy_geometry.json'),encoding='utf-8'))
src=data['source_ring_xy_m']; model=data['existing_asset_base_xy_m']
W,H=1400,1100; margin=100
allpts=src+model; xs=[p[0] for p in allpts]; ys=[p[1] for p in allpts]
lo_x=min(xs)-2; hi_x=max(xs)+2; lo_y=min(ys)-2; hi_y=max(ys)+2
scale=min((W-2*margin)/(hi_x-lo_x),(H-2*margin)/(hi_y-lo_y))
def xy(p): return (margin+(p[0]-lo_x)*scale,H-margin-(p[1]-lo_y)*scale)
im=Image.new('RGB',(W,H),'#fbfaf6'); d=ImageDraw.Draw(im)
try: font=ImageFont.truetype('arial.ttf',25); small=ImageFont.truetype('arial.ttf',18)
except: font=ImageFont.load_default(); small=font
srcpix=[xy(p) for p in src]
modelpix=[xy(p) for p in model]
d.polygon(srcpix,fill='#ead9c8',outline='#a44832',width=5)
d.line(srcpix+[srcpix[0]],fill='#a44832',width=5)
if len(modelpix)>=3:
    c=(sum(p[0] for p in modelpix)/len(modelpix),sum(p[1] for p in modelpix)/len(modelpix))
    modelpix.sort(key=lambda p:math.atan2(p[1]-c[1],p[0]-c[0]))
    d.line(modelpix+[modelpix[0]],fill='#31698b',width=4)
for i,p in enumerate(srcpix):
    d.ellipse((p[0]-6,p[1]-6,p[0]+6,p[1]+6),fill='#a44832')
    d.text((p[0]+8,p[1]-22),str(i),fill='#702b20',font=small)
legend_y=45
d.rectangle((70,legend_y,98,legend_y+24),fill='#ead9c8',outline='#a44832',width=3)
d.text((112,legend_y-2),'Live Purdue GIS FID 783 ring (14 unique vertices)',fill='#302b28',font=font)
d.line((70,legend_y+57,98,legend_y+57),fill='#31698b',width=5)
d.text((112,legend_y+42),'Legacy asset base outline (8-vertex rectangular massing)',fill='#302b28',font=font)
d.text((70,H-46),'Campus-local approximate meters • top view • GIS ring transformed from WKID 102100/3857',fill='#4c4843',font=small)
out=os.path.join(HERE,'initial_footprint_comparison.png'); im.save(out)
print(out)
