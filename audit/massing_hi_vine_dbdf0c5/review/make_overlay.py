from PIL import Image,ImageDraw
import json,math
p='audit/massing_hi_vine_dbdf0c5/review/current_asset_footprint_xy.json'
pts=json.load(open(p)); im=Image.open('audit/massing_hi_vine_dbdf0c5/sources/world_imagery_hi_vine_2026-10-26.jpg').convert('RGB'); d=ImageDraw.Draw(im)
# inverse project using repository origin approximate (longitude scale at 40.4274)
lon0=-86.9137; lat0=40.4274; mx=111412.84*math.cos(math.radians(lat0)); my=111040.0
xy=[]
for x,y in pts:
 lon=lon0+x/mx; lat=lat0+y/my
 px=(lon-(-86.909))/(.0022)*1200
 py=(40.4269-lat)/(.0015)*1100
 xy.append((round(px),round(py)))
d.polygon(xy,outline=(255,0,0),width=4)
for i,p in enumerate(xy): d.ellipse((p[0]-3,p[1]-3,p[0]+3,p[1]+3),fill=(255,0,0))
im.save('audit/massing_hi_vine_dbdf0c5/review/current_asset_aerial_overlay.jpg',quality=92)
