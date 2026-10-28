import json,os,math
from shapely.geometry import Polygon
from PIL import Image,ImageDraw,ImageFont
HERE=os.path.dirname(__file__)
g=json.load(open(os.path.join(HERE,'final_geometry.json'),encoding='utf-8'));o=json.load(open(os.path.join(HERE,'sources','osm_way_301841601_2026-10-22.json'),encoding='utf-8'))
src=[tuple(p) for p in g['source_ring_xy_m']];nodes={n['id']:n for n in o['nodes']};c=math.cos(math.radians(40.4274));osm=[((nodes[n]['lon']+86.9137)*111412.84*c,(nodes[n]['lat']-40.4274)*111040.0) for n in o['way']['nodes']]
pg=Polygon(src);po=Polygon(osm);metrics={'feature_id':752,'source_crs':'Purdue GIS WKID 102100/latestWkid 3857 transformed to repository local approximate meters','secondary_source':'OSM way 301841601 from snapshot retrieved 2026-10-22, building=school (unnamed)','gis_local_area_m2':pg.area,'osm_local_area_m2':po.area,'intersection_over_union':pg.intersection(po).area/pg.union(po).area,'hausdorff_distance_m':pg.hausdorff_distance(po),'centroid_offset_m':pg.centroid.distance(po.centroid),'max_gis_corner_to_wallbase_vertex_error_m':g['max_source_corner_error_m'],'interpretation':'GIS and OSM outlines corroborate general location and footprint (not exact agreement); official GIS ring alone defines modeled wall-base perimeter. Neither source is survey control or independent architectural measurement.'}
json.dump(metrics,open(os.path.join(HERE,'footprint_comparison.json'),'w',encoding='utf-8'),indent=2)
W,H=1400,1100;margin=110;allp=src+osm;xs=[p[0] for p in allp];ys=[p[1] for p in allp];lx=min(xs)-3;hx=max(xs)+3;ly=min(ys)-3;hy=max(ys)+3;s=min((W-2*margin)/(hx-lx),(H-2*margin)/(hy-ly))
def xy(p):return (margin+(p[0]-lx)*s,H-margin-(p[1]-ly)*s)
im=Image.new('RGB',(W,H),'#fbfaf6');d=ImageDraw.Draw(im)
try:f=ImageFont.truetype('arial.ttf',23);sm=ImageFont.truetype('arial.ttf',18)
except:f=ImageFont.load_default();sm=f
sp=[xy(p) for p in src];op=[xy(p) for p in osm]
d.polygon(sp,fill='#f1d5c7',outline='#a44832',width=5);d.line(sp+[sp[0]],fill='#a44832',width=5)
d.line(op+[op[0]],fill='#246797',width=4)
d.rectangle((60,36,90,60),fill='#f1d5c7',outline='#a44832',width=3);d.text((104,33),'Purdue GIS FID 752 (modeled wall base overlaid)',font=f,fill='#302b28')
d.line((60,91,90,91),fill='#246797',width=5);d.text((104,78),'OSM way 301841601 (unnamed; secondary cross-check)',font=f,fill='#302b28')
d.text((60,H-50),f"GIS vs OSM: IoU {metrics['intersection_over_union']:.3f} • Hausdorff {metrics['hausdorff_distance_m']:.2f} m • center offset {metrics['centroid_offset_m']:.2f} m",font=sm,fill='#4c4843')
out=os.path.join(HERE,'final_footprint_comparison.png');im.save(out);print(json.dumps(metrics));print(out)
