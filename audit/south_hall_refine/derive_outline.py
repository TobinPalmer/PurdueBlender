"""Derive a South Hall local-coordinate outline from Purdue GIS FID 528."""
import json, math
from pathlib import Path
from shapely.geometry import Polygon, shape

ROOT=Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
RAW=ROOT/"audit/south_hall_refine/raw_south_hall_fid528.geojson"
REF=ROOT/"audit/official_building_references.json"
OUT=ROOT/"audit/south_hall_refine/gis_footprint_r1.json"
ORIGIN_LAT,ORIGIN_LON=40.4274,-86.9137
PLACE_X,PLACE_Y=-1091.6500244140625,-131.2249984741211
X_SCALE=111412.84*math.cos(math.radians(ORIGIN_LAT))
Y_SCALE=111040.0

raw=json.loads(RAW.read_text(encoding="utf-8"))
assert len(raw.get("features",[]))==1, "Expected one feature FID 528"
feature=raw["features"][0]
props=feature["properties"]
assert props["FID"]==528 and props["BLDG_ABBR"]=="SH" and props["BUILDING_N"]=="South Hall"
assert props["NUM_LEVELS"]==8
source_geom=shape(feature["geometry"])
# Convert official geographic coordinates with the project-prescribed local approximation.
def project_ring(ring):
    return [[(lon-ORIGIN_LON)*X_SCALE-PLACE_X,
             (lat-ORIGIN_LAT)*Y_SCALE-PLACE_Y] for lon,lat in ring]
geo_rings=feature["geometry"]["coordinates"]
projected=Polygon(project_ring(geo_rings[0]),[project_ring(r) for r in geo_rings[1:]])
assert projected.is_valid and projected.area>0
simplified=projected.simplify(0.5,preserve_topology=True)
assert simplified.is_valid
# Verify against the checked-in official reference's processed coordinate snapshot.
refs=json.loads(REF.read_text(encoding="utf-8"))
ref=next(b for b in refs["buildings"] if b.get("fid")==528 and b.get("code")=="SH")
refpoly=Polygon([[x-PLACE_X,y-PLACE_Y] for x,y in ref["rings_xy_m"][0]])
assert projected.hausdorff_distance(refpoly)<0.03, projected.hausdorff_distance(refpoly)
area_delta=(projected.area-simplified.area)/projected.area
haus=projected.hausdorff_distance(simplified)
assert abs(area_delta)<0.002 and haus<0.51
coords=[[round(x,5),round(y,5)] for x,y in list(simplified.exterior.coords)]
record={
  "building_id":"south_hall","building_name":"South Hall","official_code":"SH","source_feature_id":528,
  "source_url":"https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D528&outFields=*&returnGeometry=true&outSR=4326&f=geojson",
  "source_provider":"Purdue University campus-map linked BuildingShapesZip4 ArcGIS FeatureServer",
  "retrieved_date":"2026-10-25","source_snapshot":"audit/south_hall_refine/raw_south_hall_fid528.geojson",
  "source_crs":"EPSG:4326 returned explicitly by the feature query; original layer is EPSG:3857 (WKID 102100)",
  "coordinate_transform":{"origin_lat":ORIGIN_LAT,"origin_lon":ORIGIN_LON,"x_formula":"(longitude - origin_lon) * 111412.84 * cos(radians(origin_lat))","y_formula":"(latitude - origin_lat) * 111040.0","units":"metres; project local approximate geographic conversion, not surveyed CRS","placement_origin_xy_m":[PLACE_X,PLACE_Y]},
  "source_date":"feature dates are blank; retrieved 2026-10-25; current built condition additionally checked against 2026 Purdue Housing photo",
  "source_properties":{"name":props["BUILDING_N"],"abbreviation":props["BLDG_ABBR"],"address":props["ADDRESS"],"num_levels":props["NUM_LEVELS"],"area_source_units":props["Shape__Area"],"perimeter_source_units":props["Shape__Length"],"global_id":props["GlobalID"]},
  "outline_method":"transform official geographic polygon, simplify with Shapely 2.2 topology-preserving tolerance 0.50 m; compare to campus-map processed snapshot",
  "outline_metrics":{"raw_vertices":len(geo_rings[0]),"simplified_vertices":len(coords)-1,"projected_area_m2":projected.area,"simplified_area_m2":simplified.area,"area_fraction_change":area_delta,"hausdorff_distance_m":haus,"bounds_xy_local_m":[list(simplified.bounds[:2]),list(simplified.bounds[2:])],"perimeter_m":simplified.length},
  "height_status":"GIS reports eight levels and floor elevations, but level values are absolute project elevation-like attributes without verified datum interpretation; geometry roof height remains an estimate",
  "reference_status":"official campus building polygon; not a certified survey; geometry represents GIS closed footprint, not guaranteed structural-wall line",
  "local_outline_xy_m":coords
}
OUT.write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps(record["outline_metrics"],indent=2))
print("raw source CRS",raw.get("crs"),"globalID",props["GlobalID"])
