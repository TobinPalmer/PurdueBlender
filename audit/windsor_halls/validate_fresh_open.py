"""Refresh Windsor fresh-open, exact GIS-shell, and SHA validation evidence."""
import hashlib
import json
import math
import os
from shapely.geometry import Polygon

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ASSET = os.path.join(ROOT, "modular", "buildings", "massing_windsor_halls_80aeb51.blend")
SOURCE = os.path.join(HERE, "sources", "purdue_gis_windsor_fids_63_66_277_278_2026-10-26.geojson")
RAW = os.path.join(HERE, "fresh_open_raw.json")
OUT = os.path.join(HERE, "validation.json")
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137
PLACEMENT_XY = (-617.8, -96.6)

def project_ring(coords):
    return [((lon-ORIGIN_LON)*111412.84*math.cos(math.radians(ORIGIN_LAT))-PLACEMENT_XY[0],
             (lat-ORIGIN_LAT)*111040.0-PLACEMENT_XY[1]) for lon,lat,*_ in coords[:-1]]

source=json.load(open(SOURCE,encoding="utf-8"))
raw=json.load(open(RAW,encoding="utf-8"))
prev=json.load(open(OUT,encoding="utf-8")) if os.path.exists(OUT) else {}
by_fid={f["properties"]["FID"]:f for f in source["features"]}
source_polys={fid:Polygon(project_ring(feature["geometry"]["coordinates"][0])) for fid,feature in by_fid.items()}
shell_polys={int(fid):Polygon(points) for fid,points in raw["structural_shell_xy"].items()}
components={}
for fid in (63,64,65,66):
    src=source_polys[fid]; mesh=shell_polys[fid]
    prior=prev.get("components",{}).get(str(fid),{})
    props=by_fid[fid]["properties"]
    union=src.union(mesh).area
    components[str(fid)]={
        "name":props.get("BUILDING_N",prior.get("name")),
        "abbreviation":props.get("BLDG_ABBR",prior.get("abbreviation")),
        "source_ring_vertices":len(src.exterior.coords)-1,
        "mesh_shell_vertices":len(mesh.exterior.coords)-1,
        "source_area_m2":src.area,
        "mesh_area_m2":mesh.area,
        "footprint_intersection_over_union":src.intersection(mesh).area/union if union else 0.0,
        "hausdorff_boundary_error_m":src.boundary.hausdorff_distance(mesh.boundary),
        "bounds_m":{"xmin":src.bounds[0],"ymin":src.bounds[1],"xmax":src.bounds[2],"ymax":src.bounds[3]},
        "source_elevation_value_unit_not_published":props.get("Elevation"),
        "gis_num_levels":props.get("NUM_LEVELS"),
        "gis_extrution_raw":props.get("Extrution"),
    }
relationships={}
ids=(63,64,65,66,277,278)
for i,a in enumerate(ids):
    for b in ids[i+1:]:
        pa,pb=source_polys[a],source_polys[b]
        relationships[f"{a}-{b}"]={"area_intersection_m2":pa.intersection(pb).area,"distance_m":pa.distance(pb),"touches":pa.touches(pb)}
validation={
    "sha256":hashlib.sha256(open(ASSET,"rb").read()).hexdigest(),
    "asset":"modular/buildings/massing_windsor_halls_80aeb51.blend",
    "fresh_open":raw,
    "footprint_comparison_method":"Shapely polygon IoU and Hausdorff boundary distance; official FID polygons and fresh-open structural shell bottom rings transformed to local coordinates using the documented approximate campus transform and placement origin",
    "components":components,
    "source_polygon_relationships_included_and_adjacent":relationships,
    "source_crs":"EPSG:4326",
    "retrieval_date":"2026-10-26",
    "included_fids":[63,64,65,66],
    "excluded_fids":[277,278],
    "coordinate_system":"local building meters; X east, Y north, Z up",
    "placement_origin_campus_xy_m":list(PLACEMENT_XY),
}
json.dump(validation,open(OUT,"w",encoding="utf-8"),indent=2)
print("validated",OUT,validation["sha256"])
for fid,row in components.items():print(fid,"IoU",row["footprint_intersection_over_union"],"Hausdorff m",row["hausdorff_boundary_error_m"])
