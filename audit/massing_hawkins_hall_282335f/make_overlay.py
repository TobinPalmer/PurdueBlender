from PIL import Image,ImageDraw,ImageFont
import json, math
from pathlib import Path
root=Path('audit/massing_hawkins_hall_282335f'); sources=root/'sources'
im=Image.open(sources/'indiana_current_aerial_hawkins.jpg').convert('RGB')
d=ImageDraw.Draw(im)
geo=json.load(open(sources/'purdue_building_shapes_fid83_2026-10-26.json'))['features'][0]['geometry']['rings'][0]
asset=json.load(open(root/'current_asset_geometry.json'))['bottom_ring_local_campus_m']
# project local feet? convert WGS through documented approximation reverse
lat0,lon0=40.4274,-86.9137
bbox=(-86.9125,40.4221,-86.9112,40.4235)
W,H=im.size

def xy_from_lonlat(lon,lat): return ((lon-bbox[0])/(bbox[2]-bbox[0])*W,(bbox[3]-lat)/(bbox[3]-bbox[1])*H)
def lonlat_from_local(x,y): return (x/(111412.84*math.cos(math.radians(40.4274)))+lon0,y/111040.0+lat0)
pts=[xy_from_lonlat(lon,lat) for lon,lat in geo]
d.line(pts,fill=(255,40,40),width=5,joint='curve')
# close polygon
if pts[0]!=pts[-1]: d.line([pts[-1],pts[0]],fill=(255,40,40),width=5)
pts2=[xy_from_lonlat(*lonlat_from_local(x,y)) for x,y in asset]
d.line(pts2,fill=(30,255,255),width=3,joint='curve')
if pts2[0]!=pts2[-1]: d.line([pts2[-1],pts2[0]],fill=(30,255,255),width=3)
d.rectangle((10,10,430,78),fill=(0,0,0))
d.text((18,17),'Official Purdue building polygon FID 83 (red)',fill=(255,60,60))
d.text((18,43),'Original asset structural outline (cyan)',fill=(30,255,255))
im.save(root/'site_alignment_overlay.png')
