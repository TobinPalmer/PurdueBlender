"""Project the ArcGIS/OSM footprints into Purdue's working campus coordinates."""
import json
from pathlib import Path
from shapely.geometry import Polygon
from shapely.geometry import box
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
GEO = json.loads((OUT / "fid852_geojson_raw.json").read_text(encoding="utf-8-sig"))
OSM = json.loads((OUT / "osm_way_117396617_raw.json").read_text(encoding="utf-8-sig"))
ring = GEO["features"][0]["geometry"]["coordinates"][0]
project = [[(lon + 86.9137) * 84810.60416539927, (lat - 40.4274) * 111040.0] for lon, lat in ring]
poly = Polygon(project)
center = poly.centroid
local = [[x - center.x, y - center.y] for x, y in project]
local_poly = Polygon(local)
part_polys = {
    "original_church_west": local_poly.intersection(box(-30, -8, -3, 40)),
    "new_church_addition_east": local_poly.intersection(box(-3, -8, 30, 40)),
    "office_classroom_addition_south": local_poly.intersection(box(-30, -40, 30, -8)),
}
osm_nodes = {e["id"]: e for e in OSM["elements"] if e["type"] == "node"}
osm_way = next(e for e in OSM["elements"] if e["type"] == "way" and e["id"] == 117396617)
osm_project = [[(osm_nodes[i]["lon"] + 86.9137) * 84810.60416539927,
                (osm_nodes[i]["lat"] - 40.4274) * 111040.0] for i in osm_way["nodes"]]
osm_poly = Polygon(osm_project)
comparison = {
    "retrieved_utc_date": "2026-10-25",
    "project_origin_xy_m": [center.x, center.y],
    "projected_outline_area_m2": poly.area,
    "projected_outline_perimeter_m": poly.length,
    "projected_bounds_world_m": [[poly.bounds[0], poly.bounds[2]], [poly.bounds[1], poly.bounds[3]]],
    "local_outline_xy_m": local,
    "component_partition_note": "The parish describes three connected buildings. Their precise joints were not identified in registered plans, so these three footprint regions are an explicitly approximate design partition of the authoritative continuous GIS/OSM outline: north/west church, north/east addition, and south office/classroom wing.",
    "footprint_parts_local_xy_m": {name: list(part.exterior.coords) for name, part in part_polys.items()},
    "gis": {"service": "BuildingShapesZip4/FeatureServer/0", "feature_id": 852,
            "name": "St. Thomas Aquinas Center", "address": "535 STATE ST",
            "native_crs": "EPSG:3857 (WKID 102100; service metadata)",
            "queried_geometry_crs": "EPSG:4326", "converted_to": "Purdue local approx XY meters",
            "area_field_value_units_not_confirmed": GEO["features"][0]["properties"]["Shape__Area"],
            "planar_area_projected_m2": poly.area,
            "url": "https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/852"},
    "osm": {"way_id": 117396617, "name": osm_way["tags"].get("name"), "tags": osm_way["tags"],
            "converted_bounds_world_m": [[min(p[0] for p in osm_project), max(p[0] for p in osm_project)],
                                          [min(p[1] for p in osm_project), max(p[1] for p in osm_project)]],
            "projected_plan_iou_with_gis": poly.intersection(osm_poly).area / poly.union(osm_poly).area,
            "url": "https://www.openstreetmap.org/way/117396617"},
    "uncertainty": ["Campus GIS polygon is an outline reference, not a surveyed wall line or as-built plan.",
                    "Three connected components and their detailed internal limits are identified by the parish, but no registered current building plan was found.",
                    "Heights and roof pitches are visual estimates from public photos; Street View was unavailable at the queried panorama."]
}
(OUT / "projected_footprint_evidence.json").write_text(json.dumps(comparison, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# A compact visual plan evidence sheet showing the authoritative map outline and original massing bounds.
w, h = 1000, 1000
im = Image.new("RGB", (w, h), "#f6f4ee")
d = ImageDraw.Draw(im)
minx, miny, maxx, maxy = poly.bounds
pad = 90
scale = min((w - 2 * pad) / (maxx - minx), (h - 2 * pad) / (maxy - miny))
def screen(p):
    return (pad + (p[0] - minx) * scale, h - pad - (p[1] - miny) * scale)
draw_points = [screen(p) for p in project]
d.polygon(draw_points, fill="#d2aa83", outline="#5c2419", width=5)
for i, p in enumerate(draw_points[:-1]):
    d.ellipse((p[0]-3, p[1]-3, p[0]+3, p[1]+3), fill="#241c18")
d.text((24, 18), "St. Thomas Aquinas Center — GIS footprint (FID 852)", fill="#1e1d1b")
d.text((24, 42), f"Source area field {GEO['features'][0]['properties']['Shape__Area']} (units unconfirmed); projected outline {poly.area:.1f} m²", fill="#1e1d1b")
d.text((24, 67), f"Project-local origin: X {center.x:.3f} m, Y {center.y:.3f} m; North is up", fill="#1e1d1b")
d.line((w-140, h-90, w-140, h-210), fill="#1e1d1b", width=5)
d.polygon([(w-140,h-230),(w-153,h-205),(w-127,h-205)], fill="#1e1d1b")
d.text((w-156, h-68), "N", fill="#1e1d1b")
d.text((24,h-52), "Footprint polygon is not an as-built wall survey; vertical form remains photo-estimated.", fill="#1e1d1b")
im.save(OUT / "gis_footprint_plan.png")
print(json.dumps({"origin_xy_m": comparison["project_origin_xy_m"], "area_m2": poly.area,
                  "bounds_world_m": comparison["projected_bounds_world_m"],
                  "osm_gis_plan_iou": comparison["osm"]["projected_plan_iou_with_gis"]}, indent=2))
