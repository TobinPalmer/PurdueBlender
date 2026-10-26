from PIL import Image, ImageDraw
import json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
img=Image.open(root/'audit/purdue_football_performance_complex/sources/esri_world_imagery_context_2026-10-26.jpg').convert('RGBA')
bbox=(-86.91901666666668,40.4338,-86.91448333333335,40.4372)
w,h=img.size
ring=json.loads((root/'audit/purdue_football_performance_complex/sources/purdue_gis_fpc_fid1202_2026-10-26.geojson').read_text())['features'][0]['geometry']['coordinates'][0]
pts=[]
for lon,lat in ring:
 x=(lon-bbox[0])/(bbox[2]-bbox[0])*w
 y=(bbox[3]-lat)/(bbox[3]-bbox[1])*h
 pts.append((x,y))
d=ImageDraw.Draw(img)
d.line(pts+[pts[0]],fill=(255,35,25,255),width=5)
for i,(x,y) in enumerate(pts[:-1]): d.ellipse((x-3,y-3,x+3,y+3),fill=(255,255,0,255))
out=root/'audit/purdue_football_performance_complex/gis_footprint_on_esri_imagery.png'
img.convert('RGB').save(out)
print(out)
