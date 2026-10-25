import json,math
from pathlib import Path
from PIL import Image,ImageDraw
A=Path(__file__).resolve().parent; img=Image.open(A/'indiana_current_orthophoto.jpg').convert('RGB'); W,H=img.size; rq=json.load(open(A/'orthophoto_request.json',encoding='utf-8')); bbox=rq['bbox'];lat0=40.4274;lon0=-86.9137
def local(x,y): return (lon0+x/(111412.84*math.cos(math.radians(lat0))),lat0+y/111040)
def merc(lon,lat): return lon*20037508.342789244/180,math.log(math.tan((90+lat)*math.pi/360))/(math.pi/180)*20037508.342789244/180
def px(x,y):
 lon,lat=local(x,y); mx,my=merc(lon,lat);return (int((mx-bbox[0])/(bbox[2]-bbox[0])*W),int((bbox[3]-my)/(bbox[3]-bbox[1])*H))
d=ImageDraw.Draw(img)
# grid lines every 20 m across source area
for x in range(-840,-639,20):
 p1=px(x,0);p2=px(x,230);d.line([p1,p2],fill=(30,90,255),width=2);d.text((p1[0]+2,20),f'X{x}',fill=(255,255,0),stroke_width=2,stroke_fill=(0,0,0))
for y in range(0,241,20):
 p1=px(-830,y);p2=px(-660,y);d.line([p1,p2],fill=(30,90,255),width=2);d.text((10,p1[1]+3),f'Y{y}',fill=(255,255,0),stroke_width=2,stroke_fill=(0,0,0))
img.save(A/'orthophoto_local_grid.jpg',quality=94)
print('saved',img.size,'origin pixel',px(0,0))
