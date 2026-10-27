"""Register Purdue GIS and OSM TREC footprints to Indiana 2023 orthophoto."""

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
GIS = HERE / "sources" / "purdue_gis_trec_oid312_2026-10-26.geojson"
OSM = HERE / "sources" / "osm_trec_way_283275002_2026-10-26.json"
ORTHO = HERE / "sources" / "indiana_2023_orthophoto_trec.jpg"
OVERLAY = HERE / "orthophoto_footprint_overlay.png"
REPORT = HERE / "footprint_imagery_comparison.json"

# Exact extent submitted to Indiana's ImageServer exportImage operation.
BBOX = (-9676470.0, 4928260.0, -9676210.0, 4928520.0)
R = 6378137.0


def webmerc(lon, lat):
    x = math.radians(lon) * R
    y = R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    return x, y


def gis_ring():
    data = json.loads(GIS.read_text(encoding="utf-8-sig"))
    feature = data["features"][0]
    return feature["properties"], [webmerc(*p) for p in feature["geometry"]["coordinates"][0]]


def osm_ring():
    data = json.loads(OSM.read_text(encoding="utf-8-sig"))
    nodes = {e["id"]: e for e in data["elements"] if e["type"] == "node"}
    way = next(e for e in data["elements"] if e["type"] == "way")
    return [webmerc(nodes[n]["lon"], nodes[n]["lat"]) for n in way["nodes"]]


def pixels(ring, size):
    xmin, ymin, xmax, ymax = BBOX
    w, h = size
    return [(round((x - xmin) / (xmax - xmin) * (w - 1)),
             round((ymax - y) / (ymax - ymin) * (h - 1))) for x, y in ring]


def area(points):
    return abs(sum(points[i][0] * points[(i + 1) % len(points)][1] -
                   points[(i + 1) % len(points)][0] * points[i][1]
                   for i in range(len(points))) / 2)


def main():
    props, gis = gis_ring()
    osm = osm_ring()
    img = Image.open(ORTHO).convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")
    draw.line(pixels(osm, img.size), fill=(0, 95, 255, 255), width=4)
    draw.line(pixels(gis, img.size), fill=(255, 32, 32, 255), width=4)
    draw.text((22, 20), "Purdue GIS OID 312 (red); OSM 283275002 (blue)",
              fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 255))
    img.save(OVERLAY)
    gis_m = [((x / R) * 180 / math.pi, (2 * math.atan(math.exp(y / R)) - math.pi / 2) * 180 / math.pi) for x, y in gis]
    osm_m = [((x / R) * 180 / math.pi, (2 * math.atan(math.exp(y / R)) - math.pi / 2) * 180 / math.pi) for x, y in osm]
    # The rings are converted to the project coordinate frame for geometric comparisons.
    def campus(points):
        return [((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
                 (lat - 40.4274) * 111040.0) for lon, lat in points]
    gis_c, osm_c = campus(gis_m), campus(osm_m)
    gb = [[min(p[i] for p in gis_c), max(p[i] for p in gis_c)] for i in range(2)]
    ob = [[min(p[i] for p in osm_c), max(p[i] for p in osm_c)] for i in range(2)]
    report = {
        "orthophoto": {
            "source": "Indiana Geographic Information Office, Indiana 2023 Imagery ImageServer",
            "acquisition": "2023 statewide orthophotography cycle, spring imagery for the western tier",
            "crs": "EPSG:3857",
            "bbox_web_mercator_m": list(BBOX),
            "image_size_px": list(img.size),
        },
        "feature_identity": {"name": props["Name"], "abbr": props["ABBR"], "objectid": props["OBJECTID"]},
        "registration": {
            "official_purdue_gis_overlay_color": "red",
            "osm_2021_overlay_color": "blue",
            "visual_result": "Both footprints lie over the same long north-south light-roofed field hall in the orthophoto. Purdue GIS OID 312 is shifted about 2.4 m west and 0.44 m south from the 2021 OSM outline, and is about 1.21 m narrower east-west; red/blue separation is visible along the perimeter and does not alter facility identity.",
            "purdue_gis_bounds_project_m": gb,
            "osm_bounds_project_m": ob,
            "dimension_comparison_m": {
                "purdue_gis_east_west_width": gb[0][1] - gb[0][0],
                "osm_east_west_width": ob[0][1] - ob[0][0],
                "gis_minus_osm_width": (gb[0][1] - gb[0][0]) - (ob[0][1] - ob[0][0]),
                "purdue_gis_north_south_length": gb[1][1] - gb[1][0],
                "osm_north_south_length": ob[1][1] - ob[1][0],
                "gis_minus_osm_length": (gb[1][1] - gb[1][0]) - (ob[1][1] - ob[1][0]),
            },
            "gis_minus_osm_center_m": [
                (gb[0][0] + gb[0][1] - ob[0][0] - ob[0][1]) / 2,
                (gb[1][0] + gb[1][1] - ob[1][0] - ob[1][1]) / 2,
            ],
            "gis_ring_area_project_m2": area(gis_c[:-1]),
            "osm_ring_area_project_m2": area(osm_c[:-1]),
            "reported_area_comparison_sqft": {
                "purdue_gis_ring_area_computed": area(gis_c[:-1]) / 0.09290304,
                "purdue_gis_squarefootage_attribute": props["squarefootage"],
                "recwell_project_size_fact_sheet": 29037,
                "status": "unresolved; likely differing area conventions, not enough evidence to reconcile",
            },
            "roof_observation": "Orthophoto shows a long north-south roof ridge, two sloped planes and repeated light-colored east-west bands perpendicular to the ridge. The roof appears white/light gray. Roof heights are not measurable from this orthographic image.",
        },
        "overlay_file": OVERLAY.name,
        "limitations": [
            "Orthophoto verifies plan position and rooftop outline only; it does not show elevations or exact wall/entrance locations.",
            "GIS/OSM footprint difference remains unresolved at the perimeter; the rebuild follows the named current Purdue GIS record.",
        ],
    }
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
