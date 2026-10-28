import json, os
from PIL import Image, ImageDraw, ImageFont
HERE=os.path.dirname(__file__)
g=json.load(open(os.path.join(HERE,'final_geometry.json'),encoding='utf-8'))
src=g['source_ring_xy_m']; model=g['model_z0_xy_m']
W,H=1400,1100; margin=100
allp=src+model; xs=[p[0] for p in allp]; ys=[p[1] for p in allp]
lo_x=min(xs)-2; hi_x=max(xs)+2; lo_y=min(ys)-2; hi_y=max(ys)+2
scale=min((W-2*margin)/(hi_x-lo_x),(H-2*margin)/(hi_y-lo_y))
def xy(p): return (margin+(p[0]-lo_x)*scale,H-margin-(p[1]-lo_y)*scale)
im=Image.new('RGB',(W,H),'#fbfaf6'); d=ImageDraw.Draw(im)
try: font=ImageFont.truetype('arial.ttf',25); small=ImageFont.truetype('arial.ttf',18)
except: font=ImageFont.load_default(); small=font
sp=[xy(p) for p in src]; mp=[xy(p) for p in model]
d.polygon(sp,fill='#ead9c8',outline='#a44832',width=6); d.line(sp+[sp[0]],fill='#a44832',width=6)
d.line(mp+[mp[0]],fill='#2566a4',width=3)
d.rectangle((70,45,98,69),fill='#ead9c8',outline='#a44832',width=3)
d.text((112,43),'Official Purdue GIS FID 783 perimeter',fill='#302b28',font=font)
d.line((70,102,98,102),fill='#2566a4',width=5)
d.text((112,87),'Rebuilt wall-base perimeter (overlays source)',fill='#302b28',font=font)
d.text((70,H-46),f"14 source vertices • max corner fit error {g['max_gis_corner_nearest_error_m']:.5f} m • approximate campus-local transform",fill='#4c4843',font=small)
out=os.path.join(HERE,'final_footprint_comparison.png'); im.save(out); print(out)
