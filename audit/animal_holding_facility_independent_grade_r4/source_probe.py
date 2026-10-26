"""Independent recomputation of AHF footprint placement and NDHM roof statistics."""
import json, math
from pathlib import Path
from PIL import Image
from shapely.geometry import Point, Polygon

root = Path(__file__).resolve().parents[2]
src = root / "audit/animal_holding_facility/sources"
ring4326 = json.loads((src / "purdue_gis_fid266_2026-10-25.json").read_text(encoding="utf-8-sig"))
ring = ring4326["features"][0]["geometry"]["rings"][0][:-1]
lat0 = math.radians(40.4274)
xy = [((lon + 86.9137) * 111412.84 * math.cos(lat0), (lat - 40.4274) * 111040.0) for lon,lat in ring]
minx,maxx = min(x for x,y in xy),max(x for x,y in xy)
miny,maxy = min(y for x,y in xy),max(y for x,y in xy)
indiana = json.loads((src / "indiana_lidar_footprints_2026-10-25.json").read_text(encoding="utf-8-sig"))
iring = indiana["features"][0]["geometry"]["rings"][0][:-1]
ixy = [((lon + 86.9137) * 111412.84 * math.cos(lat0), (lat - 40.4274) * 111040.0) for lon,lat in iring]
pp, ip = Polygon(xy), Polygon(ixy)
boundary_residual = max(max(Point(p).distance(ip.boundary) for p in xy), max(Point(p).distance(pp.boundary) for p in ixy))

# Raster georeferencing is from the saved GeoTIFF metadata and public source record.
ring2968 = json.loads((src / "purdue_gis_fid266_2026-10-25_stateplane_2968.json").read_text(encoding="utf-8-sig"))
poly2968 = Polygon(ring2968["features"][0]["geometry"]["rings"][0])
im = Image.open(src / "indiana_lidar_ndhm_tippecanoe_2018_tile_in2018_29951880_12.tif")
assert im.size == (1000,1000), im.size
ox,oy,step = 2995000.0,1885000.0,5.0
split_y = 1883168.8443683232
zones = {"north_main":[],"south_addition":[]}
for row in range(im.height):
    y = oy-(row+0.5)*step
    for col in range(im.width):
        x = ox+(col+0.5)*step
        if not poly2968.contains(Point(x,y)):
            continue
        val=float(im.getpixel((col,row)))
        if val <= -10:
            continue
        zones["north_main" if y > split_y else "south_addition"].append(val)
def stat(values):
    s=sorted(values)
    q=lambda p:s[round((len(s)-1)*p)]
    ft_to_m=1200/3937
    return {"count":len(s),"median_ft":q(.5),"median_m":q(.5)*ft_to_m,
            "q25_ft":q(.25),"q75_ft":q(.75),"iqr_m":(q(.75)-q(.25))*ft_to_m}
result={
  "purdue_fid":266,
  "purdue_local_xy_bounds_m":[[minx,maxx],[miny,maxy]],
  "purdue_local_xy_centroid_m":[Polygon(xy).centroid.x,Polygon(xy).centroid.y],
  "indiana_2018_feature_id":407881,
  "indiana_2018_centroid_offset_m":pp.centroid.distance(ip.centroid),
  "max_symmetric_vertex_to_other_boundary_m":boundary_residual,
  "indiana_ndhm_pixel_counts_and_stats":{k:stat(v) for k,v in zones.items()},
  "tile_size_px":list(im.size),"split_y_epsg2968_ft":split_y,
  "footprint_method":"independent point-in-polygon test at cell centers, official EPSG:2968 Purdue exterior ring, 5-ft NDHM tile origin and scale",
  "vertical_conversion":"US survey feet to meters using 1200/3937"
}
out=Path(__file__).resolve().parent/"source_probe.json"
out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))
