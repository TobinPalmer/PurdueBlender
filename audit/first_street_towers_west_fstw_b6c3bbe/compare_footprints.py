"""Compare fresh-open wall perimeter to Purdue GIS and OSM footprints."""
import json, math
from pathlib import Path
from shapely.geometry import shape, Polygon
from shapely.ops import transform
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent
ID="massing_first_street_towers_west_fstw_b6c3bbe"
LAT0,LON0=40.4274,-86.9137
def local(lon,lat,z=None):
    x=(lon+86.9137)*111412.84*math.cos(math.radians(40.4274)); y=(lat-40.4274)*111040.0
    return (x,y) if z is None else (x,y,z)
gisraw=json.loads((HERE/"sources/purdue_buildingshapeszip4_fstw_fid858_2026-10-26.geojson").read_text(encoding="utf-8"))
osmraw=json.loads((HERE/"sources/osm_way_283274997_fstw_2026-10-22.geojson").read_text(encoding="utf-8"))
fresh=json.loads((HERE/"fresh_open_validation.json").read_text(encoding="utf-8"))
gis=transform(local,shape(gisraw["features"][0]["geometry"]))
osm=transform(local,shape(osmraw["features"][0]["geometry"]))
candidate=Polygon(fresh["wall_bottom_ring_xy"])
def metrics(a,b):
    return {"area_m2":float(a.area),"bounds_xy_m":[float(x) for x in a.bounds],
      "intersection_over_union":float(a.intersection(b).area/a.union(b).area),
      "symmetric_hausdorff_m":float(a.hausdorff_distance(b)),
      "area_outside_reference_m2":float(a.difference(b).area),
      "reference_outside_area_m2":float(b.difference(a).area)}
record={
 "asset_id":ID,"local_frame":{"origin_lat":LAT0,"origin_lon":LON0,"transform":"X=(lon+86.9137)*111412.84*cos(radians(40.4274)); Y=(lat-40.4274)*111040.0; meters"},
 "gis":{"fid":858,"abbr":"FSTW","levels":6,"raw_ring_vertices":len(gisraw["features"][0]["geometry"]["coordinates"][0])-1,"area_m2":float(gis.area),"bounds_xy_m":[float(x) for x in gis.bounds]},
 "candidate_actual_wall":{"ring_vertices":len(fresh["wall_bottom_ring_xy"]),**metrics(candidate,gis)},
 "osm":{"way_id":283274997,"ring_vertices":len(osmraw["features"][0]["geometry"]["coordinates"][0])-1,**metrics(osm,gis)},
 "gis_vs_osm":{"iou":float(gis.intersection(osm).area/gis.union(osm).area),"symmetric_hausdorff_m":float(gis.hausdorff_distance(osm)),"gis_area_outside_osm_m2":float(gis.difference(osm).area),"osm_area_outside_gis_m2":float(osm.difference(gis).area)},
 "simplification_tolerance_m":.28,"note":"Candidate wall perimeter is the fresh-open Blender mesh perimeter; the local coordinate frame is approximate rather than a surveyed projected CRS."}
(HERE/"footprint_comparison.json").write_text(json.dumps(record,indent=2),encoding="utf-8")

# Map overlay: GIS fill/orange outline, candidate teal, OSM dashed blue. North is up.
W,H=1180,900; margin=85
minx=min(gis.bounds[0],osm.bounds[0]); maxx=max(gis.bounds[2],osm.bounds[2]); miny=min(gis.bounds[1],osm.bounds[1]); maxy=max(gis.bounds[3],osm.bounds[3])
s=min((W-2*margin)/(maxx-minx),(H-2*margin)/(maxy-miny)); cx=(minx+maxx)/2; cy=(miny+maxy)/2
def pix(pt): return (int(W/2+(pt[0]-cx)*s),int(H/2-(pt[1]-cy)*s))
im=Image.new("RGB",(W,H),(238,241,244)); draw=ImageDraw.Draw(im,"RGBA"); font=ImageFont.load_default()
def drawpoly(poly,fill,outline,width=4,dashed=False):
    pts=[pix(p) for p in list(poly.exterior.coords)]
    if fill: draw.polygon(pts,fill=fill)
    if not dashed: draw.line(pts,fill=outline,width=width,joint="curve")
    else:
        for a,b in zip(pts,pts[1:]):
            dx=b[0]-a[0]; dy=b[1]-a[1]; L=math.hypot(dx,dy)
            if not L: continue
            n=max(1,int(L/10))
            for k in range(0,n,2):
                t0=k/n; t1=min(1,(k+1)/n)
                draw.line((a[0]+dx*t0,a[1]+dy*t0,a[0]+dx*t1,a[1]+dy*t1),fill=outline,width=width)
drawpoly(gis,(221,122,55,54),(198,92,28,255),4)
drawpoly(candidate,None,(14,142,143,255),3)
drawpoly(osm,None,(36,77,151,255),3,True)
draw.text((35,24),"First Street Towers West — footprint evidence overlay",fill=(28,33,38),font=font)
draw.text((36,47),"Official Purdue GIS FID 858 (orange) | Candidate wall base (teal) | OSM way 283274997 (blue dashed)",fill=(35,45,54),font=font)
draw.text((36,H-54),f"GIS area {gis.area:.2f} m2 | Candidate/GIS IoU {candidate.intersection(gis).area/candidate.union(gis).area:.5f} | GIS/OSM IoU {gis.intersection(osm).area/gis.union(osm).area:.5f} | north up",fill=(35,45,54),font=font)
im.save(HERE/"fstw_footprint_source_comparison.png")
print(json.dumps(record,indent=2))
