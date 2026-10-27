from pathlib import Path
from PIL import Image,ImageDraw
import json,math
root=Path.cwd();aud=root/'audit/wiley_dining_court';src=aud/'sources';prev=aud/'previews';z=19;n=2**z
raw=json.loads((src/'purdue_gis_fid649.json').read_text(encoding='utf-8-sig'));ring=raw['features'][0]['geometry']['rings'][0];local=json.loads((src/'gis_outline_local.json').read_text(encoding='utf-8-sig'));ox,oy=local['proposed_marker_origin_world_m'];lat0,lon0=40.4274,-86.9137
lat=sum(p[1] for p in ring)/len(ring);lon=sum(p[0] for p in ring)/len(ring)
def tilexy(lon,lat):return ((lon+180)/360*n,(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n)
tx,ty=tilexy(lon,lat);cx,cy=round(tx),round(ty)
mos=Image.new('RGB',(768,768),(235,235,235))
for y in range(cy-1,cy+2):
 for x in range(cx-1,cx+2):mos.paste(Image.open(src/f'esri_{z}_{x}_{y}.jpg').convert('RGB'),((x-cx+1)*256,(y-cy+1)*256))
def px(lon,lat):gx,gy=tilexy(lon,lat);return ((gx-(cx-1))*256,(gy-(cy-1))*256)
def ll(x,y):return (lon0+x/(111412.84*math.cos(math.radians(lat0))),lat0+y/111040.)
img=mos.convert('RGBA');overlay=Image.new('RGBA',mos.size,(0,0,0,0));d=ImageDraw.Draw(overlay,'RGBA');gp=[px(*p) for p in ring];d.polygon(gp,fill=(255,35,35,50),outline=(255,25,35,255),width=3)
cp=[px(*ll(x+ox,y+oy)) for x,y in local['outline_local_xy_m']];d.line(cp+[cp[0]],fill=(20,90,255,255),width=4)
corn=[(-638.4627,102.2123),(-559.9111,102.2123),(-559.9111,149.0379),(-638.4627,149.0379)];d.line([px(*ll(x,y)) for x,y in corn+[corn[0]]],fill=(255,220,0,255),width=3)
img=Image.alpha_composite(img,overlay);d=ImageDraw.Draw(img,'RGBA');d.rectangle((4,4,750,47),fill=(0,0,0,200));d.text((12,9),'Wiley Dining Court | Purdue GIS FID 649 | Esri imagery z19',fill='white');d.text((12,27),'Red: GIS outline | blue: detailed structural shell | yellow: old rectangular massing bounds',fill=(255,255,190,255));img.convert('RGB').save(prev/'gis_candidate_footprint_overlay.jpg',quality=95)
print(prev/'gis_candidate_footprint_overlay.jpg')
