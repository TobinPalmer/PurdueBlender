"""Recompute Forney GIS/OSM comparison and produce a review overlay."""
import json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import Polygon

HERE=Path(__file__).resolve().parent
gis=json.loads((HERE/'purdue_gis_current.json').read_text(encoding='utf-8-sig'))
osm=json.loads((HERE/'openstreetmap_way_117146497_full.json').read_text(encoding='utf-8-sig'))
frny=next(f for f in gis['features'] if f['properties'].get('OBJECTID')==12)
nodes={n['id']:n for n in osm['elements'] if n['type']=='node'}
way=next(x for x in osm['elements'] if x['type']=='way' and x['id']==117146497)

def local(lon,lat):
    return ((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0)
gis_xy=[local(lon,lat) for lon,lat in frny['geometry']['coordinates'][0]]
osm_xy=[local(nodes[i]['lon'],nodes[i]['lat']) for i in way['nodes']]
old=Polygon(gis_xy); community=Polygon(osm_xy)
intersection=old.intersection(community).area
symdiff=old.symmetric_difference(community).area
old_massing=[-70.15533447265625,192.23245239257812,17.878074645996094,278.39947509765625]
gis_bounds=[min(x for x,y in gis_xy),min(y for x,y in gis_xy),max(x for x,y in gis_xy),max(y for x,y in gis_xy)]
osm_bounds=[min(x for x,y in osm_xy),min(y for x,y in osm_xy),max(x for x,y in osm_xy),max(y for x,y in osm_xy)]
metrics={
 "purdue_feature":"OBJECTID 12 / FRNY",
 "purdue_polygon_source_area_attribute_m2":frny['properties'].get('Shape.STArea()'),
 "purdue_polygon_area_after_local_conversion_m2":round(old.area,2),
 "osm_way":"117146497 version 9",
 "osm_polygon_area_after_local_conversion_m2":round(community.area,2),
 "intersection_m2":round(intersection,2),
 "intersection_as_percent_of_purdue_local_area":round(100*intersection/old.area,2),
 "intersection_as_percent_of_osm_local_area":round(100*intersection/community.area,2),
 "symmetric_difference_m2":round(symdiff,2),
 "purdue_bounds_local_m_xyxy":[round(v,3) for v in gis_bounds],
 "osm_bounds_local_m_xyxy":[round(v,3) for v in osm_bounds],
 "old_box_bounds_local_m_xyxy":[round(v,3) for v in old_massing],
 "old_box_area_m2":round((old_massing[2]-old_massing[0])*(old_massing[3]-old_massing[1]),2),
 "footprint_area_conflict_note":"The ArcGIS attribute Shape.STArea is 6261.056 m2, but its returned ring computes to a 3621.9 m2 polygon after the documented local coordinate conversion. OSM and the returned footprint polygon agree strongly in shape; the numeric area discrepancy is unresolved and is not used to rescale the asset.",
 "legacy_feature_overlap_note":"The separate 1938-1939 feature is an older FRNY record whose outline is almost wholly contained by the newer whole-building polygon; it is retained as historical context, not added as a second building."
}
(HERE/'footprint_comparison.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')

allpts=gis_xy+osm_xy
pad=6
xmin=min(p[0] for p in allpts)-pad; xmax=max(p[0] for p in allpts)+pad
ymin=min(p[1] for p in allpts)-pad; ymax=max(p[1] for p in allpts)+pad
W=1500; H=1300; scale=min((W-180)/(xmax-xmin),(H-250)/(ymax-ymin))
ox=(W-(xmax-xmin)*scale)/2; oy=H-150
def pix(p): return (int(ox+(p[0]-xmin)*scale),int(oy-(p[1]-ymin)*scale))
im=Image.new('RGB',(W,H),(250,249,245)); d=ImageDraw.Draw(im)
def draw_poly(points,color,width=6):
    q=[pix(p) for p in points]
    if q and q[0]!=q[-1]:q.append(q[0])
    d.line(q,fill=color,width=width,joint='curve')
draw_poly(gis_xy,(0,95,180),8)
draw_poly(osm_xy,(220,55,55),5)
# Original simple massing bounding rectangle, orange dashed.
b=old_massing; x0,y0,x1,y1=b
rect=[(x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0)]
for a,c in zip(rect[:-1],rect[1:]):
    ax,ay=pix(a); bx,by=pix(c); L=math.hypot(bx-ax,by-ay)
    for s in range(0,int(L),30):
        t0=s/L; t1=min((s+17)/L,1)
        d.line((int(ax+(bx-ax)*t0),int(ay+(by-ay)*t0),int(ax+(bx-ax)*t1),int(ay+(by-ay)*t1)),fill=(226,140,20),width=4)
font=ImageFont.load_default(size=24); small=ImageFont.load_default(size=18)
d.text((60,35),'FORNEY HALL | FOOTPRINT COMPARISON',font=font,fill=(35,38,42))
d.text((60,78),'Purdue campus GIS OBJECTID 12 (blue)  |  OpenStreetMap way 117146497 (red)',font=small,fill=(35,38,42))
d.text((60,108),'Old massing bounding rectangle (orange dashed) filled in the GIS notches and overstated footprint area.',font=small,fill=(35,38,42))
d.text((60,H-100),f"GIS/OSM intersection: {metrics['intersection_as_percent_of_purdue_local_area']}% of GIS area; symmetric difference {metrics['symmetric_difference_m2']} m2 (approximate local frame).",font=small,fill=(35,38,42))
im.save(HERE/'footprint_comparison.png')
print(json.dumps(metrics,indent=2))
