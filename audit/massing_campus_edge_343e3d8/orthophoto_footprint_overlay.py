from pathlib import Path
import json
from PIL import Image, ImageDraw
root=Path('.')
src=root/'audit/massing_campus_edge_343e3d8/sources'
image=Image.open(src/'indiana_2023_orthophoto_campus_edge.jpg').convert('RGB')
meta=json.loads((src/'indiana_2023_orthophoto_metadata.json').read_text(encoding='utf-8-sig'))
ext=meta['extent']; xmin,ymin,xmax,ymax=ext['xmin'],ext['ymin'],ext['xmax'],ext['ymax']; W,H=image.size

def px(lon,lat): return ((lon-xmin)/(xmax-xmin)*W,(ymax-lat)/(ymax-ymin)*H)
raw=json.loads((src/'openstreetmap_way_886359911_full.json').read_text(encoding='utf-8'))
byid={e['id']:e for e in raw['elements'] if e['type']=='node'}
way=next(e for e in raw['elements'] if e['type']=='way')
osm=[px(byid[n]['lon'],byid[n]['lat']) for n in way['nodes']]
ind=json.loads((src/'indiana_2016_2020_building_footprints_point_query_2026-10-25.json').read_text(encoding='utf-8-sig'))['features'][0]['geometry']['coordinates'][0]
ind=[px(lon,lat) for lon,lat in ind]
d=ImageDraw.Draw(image)
d.line(osm,fill=(255,40,40),width=6)
d.line(ind,fill=(30,255,80),width=4)
d.text((20,20),'OSM way 886359911 = red | Indiana 2016-20 footprint OBJECTID 407824 = green',fill='yellow',stroke_width=2,stroke_fill='black')
out=root/'audit/massing_campus_edge_343e3d8/orthophoto_footprint_overlay.png'
image.save(out)
print(out)
