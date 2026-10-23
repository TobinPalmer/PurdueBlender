from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,math
root=Path('audit/batch3_math'); regular='C:/Windows/Fonts/arial.ttf'; bold='C:/Windows/Fonts/arialbd.ttf'
# Source-plan overlay: transparent red boundaries match saved model divider coordinates.
im=Image.open(root/'plan_detail.png').convert('RGBA'); layer=Image.new('RGBA',im.size,(0,0,0,0));d=ImageDraw.Draw(layer)
# Map plan pixel crop from the traced room limits to the saved local partition segments.
# Red endpoints leave inferred door openings in the same positions as the saved model.
for x,segments in [(416,[(589,900),(965,990)]),(659,[(589,900)]),(868,[(589,900)]),(1008,[(589,900),(965,990)])]:
 for ya,yb in segments: d.line((x,ya,x,yb),fill=(235,45,66,235),width=5)
for x0,x1 in [(416,634),(712,1008)]: d.line((x0,990,x1,990),fill=(235,45,66,190),width=3)
for x0,x1 in [(416,661),(747,1008)]: d.line((x0,522,x1,522),fill=(235,45,66,190),width=3)
d.text((24,18),'2022 third-floor plan • modeled library divisions',font=ImageFont.truetype(bold,24),fill=(110,20,30,255),stroke_width=2,stroke_fill=(255,255,255,235))
d.text((24,52),'Red lines show saved partitions and inferred openings; 2025 group-room positions are inferred.',font=ImageFont.truetype(regular,17),fill=(50,50,50,255),stroke_width=2,stroke_fill=(255,255,255,230))
Image.alpha_composite(im,layer).convert('RGB').save(root/'plan_layout_overlay.png',quality=95)
# GIS / shell structural edge comparison overlay.
polyjson=json.loads((root/'gis_fid227.geojson').read_text())['features'][0]['geometry']['coordinates'][0]
lon0,lat0=-86.9137,40.4274; mx,my=-181.119995,-126.905003
poly=[((lon-lon0)*111412.84*math.cos(math.radians(lat0))-mx,(lat-lat0)*111040-my) for lon,lat in polyjson]
comps=json.loads((root/'wall_components.json').read_text())
lines=[]
for c in comps:
 x0,x1=c['x'];y0,y1=c['y']
 if x1-x0>=y1-y0:
  if x1-x0>.5: lines.append(((x0,(y0+y1)/2),(x1,(y0+y1)/2)))
 elif y1-y0>.5: lines.append((((x0+x1)/2,y0),((x0+x1)/2,y1)))
W,H=1000,1510; out=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(out)
left,right=-21,20; bottom,top=-36,36; sx=(W-120)/(right-left); sy=(H-240)/(top-bottom); s=min(sx,sy); ox=(W-s*(right-left))/2; oy=120
pt=lambda p:(int(ox+(p[0]-left)*s),int(oy+(top-p[1])*s))
d.polygon([pt(p) for p in poly],outline=(25,52,82),fill=(242,245,248),width=5)
for a,b in lines:d.line([pt(a),pt(b)],fill=(207,60,45),width=3)
font=ImageFont.truetype(regular,20); bf=ImageFont.truetype(bold,26)
d.text((40,25),'MATH structural edge check',font=bf,fill=(20,35,53))
metrics=json.loads((root/'structural_edge_comparison.json').read_text())
d.text((40,65),'GIS FID 227 polygon vs 50 source wall-prism centerlines; both are shown in asset-local metres.',font=font,fill=(45,55,65))
d.text((40,H-100),'Blue: Purdue GIS footprint outline     Red: modeled structural wall centerlines',font=font,fill=(45,55,65))
d.text((40,H-66),f"GIS→shell: {metrics['gis_boundary_to_shell_centerline']['share_<=0.25m']*100:.1f}% within 0.25 m • median {metrics['gis_boundary_to_shell_centerline']['median_m']:.2f} m • P95 {metrics['gis_boundary_to_shell_centerline']['p95_m']:.2f} m",font=font,fill=(45,55,65))
out.save(root/'structural_edge_overlay.png')
print('overlays saved',Image.open(root/'plan_layout_overlay.png').size,Image.open(root/'structural_edge_overlay.png').size)
