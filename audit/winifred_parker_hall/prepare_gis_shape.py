"""Prepare GIS-derived local polygon coordinates outside Blender."""
import json, math
from pathlib import Path
from shapely.geometry import Polygon, box
from shapely.ops import triangulate

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit/winifred_parker_hall'
feature=json.loads((AUDIT/'gis_feature_879_raw.json').read_text())['features'][0]
origin=(-544.25,42.425)
lon0=-86.9137; lat0=40.4274
ring=[]
for lon,lat in feature['geometry']['rings'][0][:-1]:
    ring.append(((lon-lon0)*111412.84*math.cos(math.radians(lat0))-origin[0],(lat-lat0)*111040.0-origin[1]))
foot=Polygon(ring)
assert foot.is_valid and foot.area>1700
ground=foot.intersection(box(-1000,28.3-origin[1],1000,1000))
geoms=[ground] if ground.geom_type=='Polygon' else list(ground.geoms)
def xy(poly): return list(poly.exterior.coords)[:-1]
def tris(poly,pts):
    ix={p:i for i,p in enumerate(pts)}; out=[]
    for tri in triangulate(poly):
        if poly.covers(tri.representative_point()):
            out.append([ix[p] for p in list(tri.exterior.coords)[:3]])
    return out
parts=[]
for g in geoms:
    pts=xy(g); parts.append({'ring':pts,'triangles':tris(g,pts)})
data={'source':'Purdue GIS FID 879 (PKRW)','source_url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0','retrieved':'2026-10-22','crs':'EPSG:4326 transformed with project local approximation then centered at manifest origin','origin_campus_xy_m':list(origin),'ring_local_xy_m':xy(foot),'roof_triangles':tris(foot,xy(foot)),'ground_components':parts,'footprint_area_m2':foot.area,'ground_area_m2':ground.area,'ground_cutoff_campus_y_m':28.3,'uncertainty':'GIS polygon is an approximate wall outline and has one ring; it is not surveyed and does not confirm ground-floor interior/retail setbacks.'}
(AUDIT/'gis_shell_geometry_candidate.json').write_text(json.dumps(data,indent=2))
print(json.dumps({'footprint_area_m2':foot.area,'ground_area_m2':ground.area,'components':len(parts),'ring_vertices':len(ring)}))
