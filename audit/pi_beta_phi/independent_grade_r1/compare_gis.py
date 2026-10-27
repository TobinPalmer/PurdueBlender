import json, math, os
from pathlib import Path
from shapely.geometry import Polygon
from pyproj import Transformer
root=Path(__file__).resolve().parents[3]
gis=json.loads((root/'audit/pi_beta_phi/sources/purdue_arcgis_fids_774_841.json').read_text())
f=next(x for x in gis['features'] if x['attributes']['FID']==774)
ring=f['geometry']['rings'][0]
trans=Transformer.from_crs('EPSG:3857','EPSG:4326',always_xy=True)
origin=(-429.57778493112545,-311.88038117902056)
lat0=math.radians(40.4274)
xy=[]
for x,y in ring:
    lon,lat=trans.transform(x,y)
    wx=(lon+86.9137)*111412.84*math.cos(lat0)
    wy=(lat-40.4274)*111040.0
    xy.append((wx-origin[0],wy-origin[1]))
gis_poly=Polygon(xy)
probe=json.loads((root/'audit/pi_beta_phi/fresh_open_validation.json').read_text())
model_poly=Polygon(probe['shell_lower_ring_local_xy_m'])
inter=model_poly.intersection(gis_poly).area
union=model_poly.union(gis_poly).area
out={'gis_area_local_m2':gis_poly.area,'model_area_local_m2':model_poly.area,'iou':inter/union,'symmetric_hausdorff_m':model_poly.hausdorff_distance(gis_poly),'centroid_delta_m':[model_poly.centroid.x-gis_poly.centroid.x,model_poly.centroid.y-gis_poly.centroid.y], 'gis_bounds':list(gis_poly.bounds),'model_bounds':list(model_poly.bounds)}
(root/'audit/pi_beta_phi/independent_grade_r1/gis_comparison.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
