import json, math
from pathlib import Path
from PIL import Image, ImageDraw
from shapely.geometry import Polygon, box
OUT=Path(__file__).parent
d=json.loads((OUT/'osm_buildings_near_faith_west.json').read_text())
e=next(x for x in d['elements'] if x.get('tags',{}).get('name')=='Faith West Community Center')
p=[((q['lon']+86.9137)*111412.84*math.cos(math.radians(40.4274)),(q['lat']-40.4274)*111040.0) for q in e['geometry']]
g=Polygon(p)
upper=g.intersection(box(-690,2170,-635,2225))
geoms=[upper] if upper.geom_type=='Polygon' else list(upper.geoms)
w,h=1200,1000; pad=50
xmin,ymin,xmax,ymax=-710,2130,-625,2240
def pix(q): return (pad+(q[0]-xmin)/(xmax-xmin)*(w-2*pad), h-pad-(q[1]-ymin)/(ymax-ymin)*(h-2*pad))
im=Image.new('RGB',(w,h),'white'); draw=ImageDraw.Draw(im)
pp=[pix(q) for q in p]; draw.line(pp+[pp[0]],fill=(30,30,30),width=5)
for geom in geoms:
    pp=[pix(q) for q in geom.exterior.coords]
    draw.polygon(pp,fill=(239,178,157),outline=(190,48,20),width=4)
    draw.line(pp+[pp[0]],fill=(190,48,20),width=4)
draw.text((30,20),'Black: OSM whole-building outline | red: proposed upper footprint',fill='black')
im.save(OUT/'source_footprint_plan.png')
print('type',g.geom_type,'valid',g.is_valid,'area',g.area,'upper',upper.geom_type,'components',len(geoms))
