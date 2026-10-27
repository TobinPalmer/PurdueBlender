"""Reproducible candidate footprint vs Purdue GIS 915 overlay and IoU.

Run from the repository root with regular Python (Pillow and Shapely required):
  python audit/life_science_ranges_greenhouse_and_service_building_c96231f/make_candidate_gis_overlay.py

The candidate polygons are read from the assigned Blender builder's literal range
and service pixel coordinates; the GIS polygon is read from the saved official
FID 915 GeoJSON snapshot. This intentionally does not use the superseded massing.
"""
import ast
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'life_science_ranges_greenhouse_and_service_building_c96231f'
BUILDER=ROOT/'modular'/'buildings'/'build_massing_life_science_ranges_greenhouse_and_service_building_c96231f.py'
GIS=AUDIT/'sources'/'purdue_gis_fid915.geojson'
IMAGE=AUDIT/'sources'/'esri_world_imagery_2026_extent.jpg'

def assigned_literals():
    tree=ast.parse(BUILDER.read_text(encoding='utf-8'))
    wanted={'RANGE_ROWS','SERVICE_PIXELS','IMAGE_BBOX','IMAGE_SIZE','GEO_ORIGIN'}
    found={}
    for node in tree.body:
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name) and target.id in wanted:
                    found[target.id]=ast.literal_eval(node.value)
    missing=wanted-found.keys()
    if missing: raise RuntimeError(f'Builder coordinate literals unavailable: {sorted(missing)}')
    return found

cfg=assigned_literals()
west,south,east,north=cfg['IMAGE_BBOX']; iw,ih=cfg['IMAGE_SIZE']; lat0,lon0=cfg['GEO_ORIGIN']
def ll_world(lon,lat):
    return ((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0)
def pixel_world(px,py):
    lon=west+(px/iw)*(east-west)
    lat=north-(py/ih)*(north-south)
    return ll_world(lon,lat)

snapshot=json.loads(GIS.read_text(encoding='utf-8'))
feature=snapshot['features'][0]
assert feature['properties']['FID']==915 and feature['properties']['BLDG_ABBR']=='LSR'
gis_rings=feature['geometry']['coordinates']
raw_gis_xy=[ [ll_world(x,y) for x,y,*_ in ring] for ring in gis_rings ]
raw_all=[p for ring in raw_gis_xy for p in ring]
placement_origin=((min(p[0] for p in raw_all)+max(p[0] for p in raw_all))/2,
                  (min(p[1] for p in raw_all)+max(p[1] for p in raw_all))/2)
gis_xy=[ [(x-placement_origin[0],y-placement_origin[1]) for x,y in ring] for ring in raw_gis_xy ]
gis_poly=Polygon(gis_xy[0],gis_xy[1:])
if not gis_poly.is_valid: gis_poly=gis_poly.buffer(0)

candidate_polys=[]
for row in cfg['RANGE_ROWS']:
    x1,y1,x2,y2=row['pixels']
    pts=[pixel_world(x1,y1),pixel_world(x2,y1),pixel_world(x2,y2),pixel_world(x1,y2)]
    pts=[(x-placement_origin[0],y-placement_origin[1]) for x,y in pts]
    candidate_polys.append(Polygon(pts))
sx1,sy1,sx2,sy2=cfg['SERVICE_PIXELS']
service_pts=[pixel_world(sx1,sy1),pixel_world(sx2,sy1),pixel_world(sx2,sy2),pixel_world(sx1,sy2)]
candidate_polys.append(Polygon([(x-placement_origin[0],y-placement_origin[1]) for x,y in service_pts]))
candidate=unary_union(candidate_polys)
intersection=candidate.intersection(gis_poly).area
union=candidate.union(gis_poly).area
iou=intersection/union if union else 0.0

# Raster overlay on the same orthorectified image used to lay out the candidate.
base=Image.open(IMAGE).convert('RGB')
if base.size!=(iw,ih):
    raise RuntimeError(f'Builder image extent is {iw}x{ih}, saved image is {base.size}')
overlay=Image.new('RGBA',base.size,(0,0,0,0)); draw=ImageDraw.Draw(overlay,'RGBA')
def ll_pixel(lon,lat): return (round((lon-west)/(east-west)*iw),round((north-lat)/(north-south)*ih))
# GIS boundary: magenta; shade the outer footprint while leaving interior rings as holes.
gis_mask=Image.new('L',base.size,0); md=ImageDraw.Draw(gis_mask)
md.polygon([ll_pixel(lon,lat) for lon,lat,*_ in gis_rings[0]],fill=100)
for hole in gis_rings[1:]: md.polygon([ll_pixel(lon,lat) for lon,lat,*_ in hole],fill=0)
purple=Image.new('RGBA',base.size,(214,35,191,0)); purple.putalpha(gis_mask)
overlay=Image.alpha_composite(overlay,purple)
draw=ImageDraw.Draw(overlay,'RGBA')
for ring in gis_rings:
    line=[ll_pixel(lon,lat) for lon,lat,*_ in ring]
    draw.line(line+[line[0]],fill=(255,55,225,255),width=4)
# Candidate greenhouse rows are cyan, separate service footprint is amber.
for idx,row in enumerate(cfg['RANGE_ROWS'],1):
    x1,y1,x2,y2=row['pixels']; pts=[(x1,y1),(x2,y1),(x2,y2),(x1,y2)]
    draw.polygon(pts,fill=(30,230,210,68),outline=(0,255,225,255),width=4)
    cx=(x1+x2)//2; cy=(y1+y2)//2
    draw.ellipse((cx-12,cy-12,cx+12,cy+12),fill=(0,40,40,230),outline=(255,255,255,255),width=2)
    draw.text((cx-5,cy-8),str(idx),fill=(255,255,255,255))
draw.polygon([(sx1,sy1),(sx2,sy1),(sx2,sy2),(sx1,sy2)],fill=(255,165,30,76),outline=(255,180,30,255),width=4)

combined=Image.alpha_composite(base.convert('RGBA'),overlay)
draw=ImageDraw.Draw(combined,'RGBA')
try: font=ImageFont.truetype('arial.ttf',20)
except OSError: font=ImageFont.load_default()
panel=(18,18,850,166); draw.rounded_rectangle(panel,radius=10,fill=(12,20,28,220),outline=(255,255,255,150),width=2)
draw.text((38,30),'LIFE SCIENCE RANGES — CURRENT CANDIDATE vs OFFICIAL GIS 915',font=font,fill=(255,255,255,255))
draw.text((38,62),'Cyan boxes = seven greenhouse row footprints from current builder; amber = service wing',font=font,fill=(60,255,230,255))
draw.text((38,92),'Magenta = official Purdue GIS FID 915 outer boundary; its internal ring is preserved',font=font,fill=(255,100,225,255))
draw.text((38,122),f'Candidate/GIS intersection-over-union = {iou:.3f}  |  candidate area {candidate.area:.1f} m²  |  GIS area {gis_poly.area:.1f} m²',font=font,fill=(255,255,255,255))

out_image=AUDIT/'previews'/'candidate_gis_footprint_overlay.png'
combined.convert('RGB').save(out_image,quality=95)
metrics={
 'candidate':'Current greenhouse row rectangles and service wing defined by assigned builder literals. This is not the superseded massing box.',
 'official_gis':{'provider':'Purdue University BuildingShapesZip4 FeatureServer layer 0','feature_id':915,'building_abbr':'LSR','geometry_type':feature['geometry']['type'],'rings':len(gis_rings)},
 'coordinate_method':'Builder pixel coordinates are mapped through its saved EPSG:4326 image extent to local XY using the exact project geographic approximation; the saved GIS GeoJSON coordinates use the same mapping. Area and IoU are calculated with Shapely in projected local meters.',
 'candidate_polygon_count':len(candidate_polys),'candidate_union_area_m2':candidate.area,'gis_polygon_area_m2':gis_poly.area,'intersection_area_m2':intersection,'union_area_m2':union,'intersection_over_union':iou,
 'candidate_bounds_local_m':[[candidate.bounds[0],candidate.bounds[2]],[candidate.bounds[1],candidate.bounds[3]]],
 'gis_bounds_local_m':[[gis_poly.bounds[0],gis_poly.bounds[2]],[gis_poly.bounds[1],gis_poly.bounds[3]]],
 'source_image_extent_lonlat':[west,south,east,north],'source_image_pixels':[iw,ih],
 'placement_origin_xy_m':list(placement_origin),
 'artifact':str(out_image.relative_to(ROOT))
}
(AUDIT/'candidate_gis_overlay_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf-8')
print(json.dumps(metrics,indent=2))
