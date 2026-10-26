"""Test whether 2018 AHF NDHM values support a spatial roof-plane profile."""
import json
from pathlib import Path

import numpy as np
from pyproj import Transformer
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "audit/animal_holding_facility/sources"
RASTER = SOURCES / "indiana_lidar_ndhm_tippecanoe_2018_tile_in2018_29951880_12.tif"
RING_JSON = SOURCES / "purdue_gis_fid266_2026-10-25_stateplane_2968.json"
OUT = ROOT / "audit/animal_holding_facility/ndhm_roof_profile_analysis.json"
ORIGIN_X_FT, ORIGIN_Y_FT, PIXEL_FT = 2995000.0, 1885000.0, 5.0
ROOF_ZONE_Y_FT = 1883168.8443683232
FT_TO_M = 1200.0 / 3937.0
BIN_SIZES_M = (2.5, 5.0, 7.5, 10.0)
TO_WGS84 = Transformer.from_crs(2968, 4326, always_xy=True)

ring = json.loads(RING_JSON.read_text(encoding="utf-8-sig"))["features"][0]["geometry"]["rings"][0]
polygon_ft = [(float(x), float(y)) for x, y in ring[:-1]]


def inside(x, y):
    flag = False
    for i, (x1, y1) in enumerate(polygon_ft):
        x2, y2 = polygon_ft[(i + 1) % len(polygon_ft)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            flag = not flag
    return flag


values = {"north_main": [], "south_addition": []}
img = Image.open(RASTER)
for row in range(img.height):
    y_ft = ORIGIN_Y_FT - (row + 0.5) * PIXEL_FT
    if abs(y_ft - 1883168.0) > 1000:
        continue
    for col in range(img.width):
        x_ft = ORIGIN_X_FT + (col + 0.5) * PIXEL_FT
        if not inside(x_ft, y_ft):
            continue
        z_ft = float(img.getpixel((col, row)))
        if z_ft <= -10:
            continue
        zone = "north_main" if y_ft > ROOF_ZONE_Y_FT else "south_addition"
        lon, lat = TO_WGS84.transform(x_ft, y_ft)
        local_x = (lon + 86.9137) * 111412.84 * np.cos(np.deg2rad(40.4274))
        local_y = (lat - 40.4274) * 111040.0
        values[zone].append((local_x, local_y, z_ft * FT_TO_M))


def fit_zone(samples, bin_m):
    samples = np.asarray(samples, dtype=float)
    origin = np.median(samples[:, :2], axis=0)
    xy = samples[:, :2] - origin
    bins = {}
    for (x, y), z in zip(xy, samples[:, 2]):
        key = (int(np.floor(x / bin_m)), int(np.floor(y / bin_m)))
        bins.setdefault(key, []).append(float(z))
    centers = np.asarray([((ix + 0.5) * bin_m, (iy + 0.5) * bin_m, np.median(zs))
                          for (ix, iy), zs in bins.items()], dtype=float)
    design = np.column_stack((centers[:, 0], centers[:, 1], np.ones(len(centers))))
    coeff, *_ = np.linalg.lstsq(design, centers[:, 2], rcond=None)
    residual = centers[:, 2] - design @ coeff
    flat = centers[:, 2] - np.median(centers[:, 2])
    mad = lambda a: float(np.median(np.abs(a - np.median(a))))
    rms = lambda a: float(np.sqrt(np.mean(a * a)))
    predicted = design @ coeff
    relative_prediction = (coeff[0] * (samples[:, 0] - origin[0]) +
                           coeff[1] * (samples[:, 1] - origin[1]))
    adjusted_c = float(np.median(samples[:, 2]) - np.median(relative_prediction))
    return {
        "sample_count": int(len(samples)),
        "spatial_bin_count": int(len(centers)),
        "bin_size_m": bin_m,
        "plane_anchor_local_xy_m": [round(float(v), 4) for v in origin],
        "plane_anchor_height_m": round(adjusted_c, 4),
        "plane_coefficients_local_z_equals_ax_plus_by_plus_c": [round(float(coeff[0]), 6), round(float(coeff[1]), 6), round(adjusted_c, 6)],
        "slope_percent_x": round(float(coeff[0] * 100), 3),
        "slope_percent_y": round(float(coeff[1] * 100), 3),
        "flat_median_absolute_residual_m": round(mad(flat), 4),
        "plane_median_absolute_residual_m": round(mad(residual), 4),
        "flat_rms_residual_m": round(rms(flat), 4),
        "plane_rms_residual_m": round(rms(residual), 4),
        "height_p05_m": round(float(np.quantile(samples[:, 2], 0.05)), 3),
        "height_median_m": round(float(np.median(samples[:, 2])), 3),
        "height_p95_m": round(float(np.quantile(samples[:, 2], 0.95)), 3),
        "interpretation": "Regression tests normalized roof-surface height spatial trend; it is not an eave survey and may reflect rooftop equipment, 5-ft gridding, edge mixing, or ground-normalization error."
    }


result = {
    "source": str(RASTER.relative_to(ROOT)).replace("\\", "/"),
    "zone_boundary_source": "2023 Indiana orthophoto roof-tone split, transformed to EPSG:2968",
    "method": "Transform each valid NDHM pixel center from EPSG:2968 to geographic coordinates and then into the project-local XY frame. Fit least-squares planes to median heights aggregated into spatial bins inside each roof zone.",
    "units": "US survey feet converted to meters; NDHM values are normalized height above local ground.",
    "zones": {name: fit_zone(samples, 5.0) for name, samples in values.items()},
    "bin_size_sensitivity": {
        name: {f"{size:g}m": {
            "slope_percent_x": fit_zone(samples, size)["slope_percent_x"],
            "slope_percent_y": fit_zone(samples, size)["slope_percent_y"],
            "plane_median_absolute_residual_m": fit_zone(samples, size)["plane_median_absolute_residual_m"],
            "flat_median_absolute_residual_m": fit_zone(samples, size)["flat_median_absolute_residual_m"],
            "spatial_bin_count": fit_zone(samples, size)["spatial_bin_count"]
        } for size in BIN_SIZES_M} for name, samples in values.items()
    },
    "limitations": [
        "The 2018 NDHM is a 5-ft surface model rather than surveyed structural roof points.",
        "The 2023 roof-zone boundary is not a surveyed seam.",
        "Spatial gradients can be caused by rooftop equipment, edge mixing, or local ground normalization; no facade, eave, or roof framing survey was found."
    ]
}
OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
