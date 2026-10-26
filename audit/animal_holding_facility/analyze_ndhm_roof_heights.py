"""Summarize Tippecanoe County 2018 NDHM pixels inside AHF's two aerial roof zones."""
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "audit/animal_holding_facility/sources"
RASTER = SOURCES / "indiana_lidar_ndhm_tippecanoe_2018_tile_in2018_29951880_12.tif"
RING_JSON = SOURCES / "purdue_gis_fid266_2026-10-25_stateplane_2968.json"
OUT = ROOT / "audit/animal_holding_facility/ndhm_roof_height_statistics.json"
ORIGIN_X_FT, ORIGIN_Y_FT, PIXEL_SIZE_FT = 2995000.0, 1885000.0, 5.0
ROOF_ZONE_Y_FT = 1883168.8443683232  # row 817 of georeferenced Indiana 2023 ortho, transformed to EPSG:2968
FEET_TO_METERS = 1200.0 / 3937.0  # U.S. survey foot

img = Image.open(RASTER)
ring = json.loads(RING_JSON.read_text(encoding="utf-8-sig"))["features"][0]["geometry"]["rings"][0]
polygon = [((x - ORIGIN_X_FT) / PIXEL_SIZE_FT, (ORIGIN_Y_FT - y) / PIXEL_SIZE_FT) for x, y in ring]

def inside(px, py):
    inside_flag = False
    for i, (x1, y1) in enumerate(polygon):
        x2, y2 = polygon[(i + 1) % len(polygon)]
        if (y1 > py) != (y2 > py) and px < (x2 - x1) * (py - y1) / (y2 - y1) + x1:
            inside_flag = not inside_flag
    return inside_flag

def quantile(sorted_values, fraction):
    return sorted_values[round((len(sorted_values) - 1) * fraction)]

values = {"all": [], "north_main": [], "south_addition": []}
for row in range(img.height):
    for col in range(img.width):
        if not inside(col + 0.5, row + 0.5):
            continue
        raw_ft = float(img.getpixel((col, row)))
        if raw_ft <= -10:
            continue
        y_ft = ORIGIN_Y_FT - (row + 0.5) * PIXEL_SIZE_FT
        zone = "north_main" if y_ft > ROOF_ZONE_Y_FT else "south_addition"
        values["all"].append(raw_ft)
        values[zone].append(raw_ft)

summary = {}
for zone, samples in values.items():
    samples.sort()
    if not samples:
        continue
    summary[zone] = {
        "pixel_count": len(samples),
        "percentile_05_ft": round(quantile(samples, 0.05), 3),
        "percentile_25_ft": round(quantile(samples, 0.25), 3),
        "median_ft": round(quantile(samples, 0.50), 3),
        "percentile_75_ft": round(quantile(samples, 0.75), 3),
        "percentile_95_ft": round(quantile(samples, 0.95), 3),
        "median_m": round(quantile(samples, 0.50) * FEET_TO_METERS, 3),
        "iqr_m": round((quantile(samples, 0.75) - quantile(samples, 0.25)) * FEET_TO_METERS, 3)
    }

result = {
    "method": "Read the 32-bit float NDHM GeoTIFF, transform the official Purdue FID266 polygon from the saved EPSG:2968 ring to the tile's 5-ft pixels, and summarize valid normalized-height cells by orthophoto roof zone. Heights are above local ground. Median is used as a robust representative roof-surface height.",
    "raster": str(RASTER.relative_to(ROOT)).replace("\\", "/"),
    "ring": str(RING_JSON.relative_to(ROOT)).replace("\\", "/"),
    "tile_origin_epsg2968_ft": [ORIGIN_X_FT, ORIGIN_Y_FT],
    "pixel_size_ft": PIXEL_SIZE_FT,
    "roof_zone_boundary_stateplane_y_ft": ROOF_ZONE_Y_FT,
    "vertical_unit_assumption": "U.S. survey feet, inherited from source Indiana 3DEP LiDAR/DTM and preserved by the normalized-height subtraction; see source record and saved 2022 paper.",
    "feet_to_meters": FEET_TO_METERS,
    "zones": summary,
    "limitations": [
        "NDHM is 5-ft grid height above ground, not a survey of eaves; pixel maxima can include rooftop equipment and edge effects.",
        "Roof-zone split comes from the 2023 orthophoto and is approximate; it is not a construction seam survey.",
        "LiDAR acquisition is 2018; the 2023 imagery confirms roof-zone continuity at a later date but not exact roof elevations in 2023."
    ]
}
OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
