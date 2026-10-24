"""Plot the 5x5 DSM-minus-DTM samples on the registered 2023 NSEL orthophoto."""
import json, math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
AUDIT=Path(__file__).resolve().parent
reg=json.loads((AUDIT/'indiana_current_orthophoto_nsel_r1_registration.json').read_text(encoding='utf-8'))
lidar=json.loads((AUDIT/'nsel_lidar_height_r1.json').read_text(encoding='utf-8'))
im=Image.open(AUDIT/'indiana_current_orthophoto_nsel_r1.jpg').convert('RGB')
draw=ImageDraw.Draw(im)
xmin,ymin,xmax,ymax=reg['request_bbox_3857'];w,h=reg['image_px']
R=6378137.0
def merc(lon,lat):
    return R*math.radians(lon),R*math.log(math.tan(math.pi/4+math.radians(lat)/2))
for s in lidar['fid242_dsm']['grid_samples']:
    lon,lat=s['lonlat'];x,y=merc(lon,lat)
    px=(x-xmin)/(xmax-xmin)*w;py=(ymax-y)/(ymax-ymin)*h
    val=s['dsm_minus_dtm_ft']
    color=(255,70,40) if val>20 else (0,80,255)
    rad=9
    draw.ellipse((px-rad,py-rad,px+rad,py+rad),fill=color,outline=(255,255,255),width=2)
    draw.text((px+10,py-7),f'{val:.1f} ft',fill=(255,255,255),stroke_width=2,stroke_fill=(0,0,0))
out=AUDIT/'nsel_lidar_height_samples_r1.jpg'
im.save(out,quality=95)
print(out)
