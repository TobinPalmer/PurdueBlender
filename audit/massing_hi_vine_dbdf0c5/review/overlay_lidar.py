from PIL import Image,ImageDraw
import json
im=Image.open('audit/massing_hi_vine_dbdf0c5/sources/world_imagery_hi_vine_2026-10-26.jpg').convert('RGB'); d=ImageDraw.Draw(im)
dat=json.load(open('audit/massing_hi_vine_dbdf0c5/sources/indiana_lidar_buildings_around_hi_vine_2026-10-26.geojson'))
for f in dat['features']:
 oid=f['properties']['objectid']; color=(255,0,0) if oid==407783 else (0,255,255)
 for ring in f['geometry']['coordinates']:
  coords=[]
  for xy in ring:
   lon,lat=map(float,xy.split()); px=(lon-(-86.909))/.0022*1200; py=(40.4269-lat)/.0015*1100; coords.append((round(px),round(py)))
  d.polygon(coords,outline=color,width=2)
  if oid==407783: d.text(coords[0],str(oid),fill=color)
im.save('audit/massing_hi_vine_dbdf0c5/review/indiana_lidar_overlay.jpg',quality=92)
