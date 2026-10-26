"""Summarize NDHM heights in orthophoto-interpreted Campus Edge roof zones."""
import json
import math
from pathlib import Path

import numpy as np
import tifffile
from PIL import Image, ImageDraw
from pyproj import Transformer
from shapely.geometry import Point, Polygon, box

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "audit/massing_campus_edge_343e3d8"
SOURCES = EVIDENCE / "sources"
RASTER = SOURCES / "indiana_2018_tippecanoe_ndhm_in2018_30001880_12.tif"
OSM = SOURCES / "openstreetmap_way_886359911_full.json"
ORTHO = SOURCES / "indiana_2023_orthophoto_campus_edge.jpg"
META = SOURCES / "indiana_2023_orthophoto_metadata.json"
INDIANA_FOOTPRINT = SOURCES / "indiana_2016_2020_building_footprints_point_query_2026-10-25.json"
OUT = EVIDENCE / "campus_edge_roof_zone_analysis.json"
FT_TO_M = 1200.0 / 3937.0
ORIGIN_X, ORIGIN_Y, PIXEL = 3000000.0, 1885000.0, 5.0
ROW_INTERVALS = {"north": (195.0, 541.0), "middle": (742.0, 978.0), "south": (1096.0, 1302.0)}

meta = json.loads(META.read_text(encoding="utf-8-sig"))
extent = meta["extent"]
width, height = meta["width"], meta["height"]
zones = {}
for name, (row_a, row_b) in ROW_INTERVALS.items():
    lat_a = extent["ymax"] - row_a / height * (extent["ymax"] - extent["ymin"])
    lat_b = extent["ymax"] - row_b / height * (extent["ymax"] - extent["ymin"])
    ya = (lat_a - 40.4274) * 111040.0
    yb = (lat_b - 40.4274) * 111040.0
    zones[name] = {"orthophoto_rows_px": [row_a, row_b], "local_y_bounds_m": [round(min(ya, yb), 3), round(max(ya, yb), 3)]}

raw = json.loads(OSM.read_text(encoding="utf-8"))
nodes = {item["id"]: item for item in raw["elements"] if item["type"] == "node"}
way = next(item for item in raw["elements"] if item["type"] == "way")
to_stateplane = Transformer.from_crs("EPSG:4326", "EPSG:2968", always_xy=True)
to_wgs84 = Transformer.from_crs("EPSG:2968", "EPSG:4326", always_xy=True)
local_outline = []
stateplane_outline = []
for node_id in way["nodes"]:
    node = nodes[node_id]
    lon, lat = node["lon"], node["lat"]
    stateplane_outline.append(to_stateplane.transform(lon, lat))
    local_outline.append(((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
                         (lat - 40.4274) * 111040.0))
outline = Polygon(local_outline)
raster = tifffile.imread(RASTER)
stateplane_polygon = Polygon(stateplane_outline)
samples = {name: [] for name in zones}
for row in range(raster.shape[0]):
    y = ORIGIN_Y - (row + 0.5) * PIXEL
    if y < stateplane_polygon.bounds[1] - PIXEL or y > stateplane_polygon.bounds[3] + PIXEL:
        continue
    for col in range(raster.shape[1]):
        x = ORIGIN_X + (col + 0.5) * PIXEL
        if x < stateplane_polygon.bounds[0] - PIXEL or x > stateplane_polygon.bounds[2] + PIXEL:
            continue
        if not stateplane_polygon.contains(Point(x, y)):
            continue
        value = float(raster[row, col])
        if not math.isfinite(value) or value < 10 or value > 160:
            continue
        lon, lat = to_wgs84.transform(x, y)
        local_y = (lat - 40.4274) * 111040.0
        for name, zone in zones.items():
            y_min, y_max = zone["local_y_bounds_m"]
            if y_min <= local_y <= y_max:
                samples[name].append(value * FT_TO_M)

for name, values in samples.items():
    array = np.asarray(values)
    zones[name]["ndhm_sample_count"] = int(array.size)
    zones[name]["height_quantiles_m"] = {str(q): round(float(np.percentile(array, q)), 3) for q in (5, 25, 50, 75, 90, 95)}
    zones[name]["roof_surface_datum_estimate_m"] = round(float(np.median(array)), 3)

result = {
    "building_id": "massing_campus_edge_343e3d8",
    "sources": {
        "orthophoto": "audit/massing_campus_edge_343e3d8/sources/indiana_2023_orthophoto_campus_edge.jpg",
        "orthophoto_metadata": "audit/massing_campus_edge_343e3d8/sources/indiana_2023_orthophoto_metadata.json",
        "ndhm": "audit/massing_campus_edge_343e3d8/sources/indiana_2018_tippecanoe_ndhm_in2018_30001880_12.tif",
        "outline": "OpenStreetMap way 886359911 (Campus Edge, 134 Pierce Street), sampled inside its EPSG:2968 polygon"
    },
    "method": "Three visibly separate roof-pad row intervals were interpreted from the 2023 orthophoto (pixel rows). Row edges are transformed using the saved EPSG:4326 orthophoto extent and the project's approximate campus local conversion; 2018 5-ft NDHM pixel centers inside the OSM polygon are summarized by the resulting Y bands. The intervals are source-georeferenced interpretations, not surveyed tower boundaries.",
    "units": "NDHM US survey feet converted to meters; values are normalized surface height above local ground.",
    "zones": zones,
    "limitations": [
        "Orthophoto rows identify approximate roof pads and recesses; metadata extent and local conversion are approximate, and roof edges need not coincide with structural footprint walls.",
        "NDHM values are a surface-height proxy, not eave or structural roof elevations; 5-ft cells mix edge, trees, and rooftop elements.",
        "Tower floor counts, internal boundaries, exact tower heights, roof parapets, and podium/courtyard elevations remain uncertain."
    ]
}
OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

# Source evidence preview: show interpreted pad strips clipped to the GIS
# outline over the orthophoto, keeping the neighboring scene visible.
image = Image.open(ORTHO).convert("RGB")
draw = ImageDraw.Draw(image, "RGBA")
feature = json.loads(INDIANA_FOOTPRINT.read_text(encoding="utf-8-sig"))["features"][0]
ring = feature["geometry"]["coordinates"][0]
outline_px = [((lon - extent["xmin"]) / (extent["xmax"] - extent["xmin"]) * width,
               (extent["ymax"] - lat) / (extent["ymax"] - extent["ymin"]) * height)
              for lon, lat in ring]
footprint_px = Polygon(outline_px)
draw.line(outline_px, fill=(50, 255, 110, 230), width=6)
palette = {"north": (35, 120, 255, 65), "middle": (225, 165, 30, 70), "south": (225, 65, 75, 65)}
for name, (row_a, row_b) in ROW_INTERVALS.items():
    clipped = footprint_px.intersection(box(0, row_a, width - 1, row_b))
    shapes = list(clipped.geoms) if hasattr(clipped, "geoms") else [clipped]
    for shape in shapes:
        if shape.is_empty or shape.geom_type != "Polygon":
            continue
        outline = [(int(x), int(y)) for x, y in shape.exterior.coords]
        draw.polygon(outline, fill=palette[name], outline=(20, 40, 245, 240), width=5)
        label_point = shape.representative_point()
        draw.text((int(label_point.x), int(label_point.y)), f"{name.title()} tower band (interpreted)",
                  fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(10, 20, 35, 255))
for row in (541, 742, 978, 1096):
    draw.line((0, row, width - 1, row), fill=(255, 205, 50, 210), width=3)
image.save(EVIDENCE / "orthophoto_roof_zone_interpretation.png")
print(json.dumps(result, indent=2))
