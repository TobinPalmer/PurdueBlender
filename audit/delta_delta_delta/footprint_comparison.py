"""Compare serialized source footprint mesh with official FID 753 geometry."""
import json, math
from shapely.geometry import Polygon
from shapely.validation import explain_validity

gis=json.load(open("audit/delta_delta_delta/sources/purdue_building_fid_753.geojson",encoding="utf-8"))["features"][0]
fresh=json.load(open("audit/delta_delta_delta/fresh_open_validation.json",encoding="utf-8"))
lat0,lon0=40.4274,-86.9137
def project(lon,lat):
    return ((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0)
source=[project(lon,lat) for lon,lat in gis["geometry"]["coordinates"][0][:-1]]
origin=fresh["expected_xy_placement_origin_m"]
asset=[(x+origin[0],y+origin[1]) for x,y in fresh["foundation_outline_local_m"]]
source_poly=Polygon(source)
asset_poly=Polygon(asset)
intersection=source_poly.intersection(asset_poly).area
union=source_poly.union(asset_poly).area
result={
  "feature_id":gis["properties"]["FID"],
  "source_crs":gis.get("crs",{}).get("properties",{}).get("name","EPSG:4326"),
  "comparison_crs":"project local XY metre approximation; origin 40.4274 N, -86.9137 E",
  "source_polygon_valid":source_poly.is_valid,
  "asset_polygon_valid":asset_poly.is_valid,
  "source_validity":explain_validity(source_poly),
  "asset_validity":explain_validity(asset_poly),
  "source_outline_vertices":len(source),
  "asset_outline_vertices":len(asset),
  "source_area_m2":source_poly.area,
  "asset_area_m2":asset_poly.area,
  "intersection_over_union":intersection/union,
  "symmetric_hausdorff_distance_m":source_poly.hausdorff_distance(asset_poly),
  "source_bounds_xy_m":list(source_poly.bounds),
  "asset_bounds_xy_m":list(asset_poly.bounds),
  "interpretation":"This checks that the saved foundation ring retains the selected GIS ring and local-origin transform. Geometry was constructed from this same GIS source, so this is a serialization/transform check, not independent confirmation that FID 753 describes the actual wall line.",
  "status":"PASS" if source_poly.is_valid and asset_poly.is_valid and source_poly.hausdorff_distance(asset_poly)<0.001 else "FAIL"
}
with open("audit/delta_delta_delta/footprint_comparison.json","w",encoding="utf-8") as f: json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
