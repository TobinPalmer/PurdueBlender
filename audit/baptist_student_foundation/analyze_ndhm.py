"""Sample the BStF footprint against the 2018 Indiana NDHM tile.

Requires numpy, tifffile, and pyproj. The tile values are U.S. survey feet.
This describes roof-surface height samples only, not measured wall/eave/ridge
heights. Pixels above 25 ft inside the automated outline are excluded as likely
canopy contamination; the cutoff is documented as a robustness choice.
"""
import json
from pathlib import Path
import numpy as np
import tifffile
from pyproj import Transformer

HERE = Path(__file__).resolve().parent
SOURCES = HERE / "sources"
FOOTPRINT = json.loads((SOURCES / "indiana_lidar_building_footprint_feature_441814_raw.json").read_text())
RING_3857 = FOOTPRINT["geometry"]["coordinates"][0][:-1]
RASTER = tifffile.imread(SOURCES / "in2018_29951885_12_ndhm.tif")
# GeoTIFF tiepoint: upper left (2,995,000, 1,890,000) ftUS; 5-ft cells.
X0_FT, Y0_FT, CELL_FT = 2995000.0, 1890000.0, 5.0
TO_GEO = Transformer.from_crs(3857, 4326, always_xy=True)
TO_STATE_PLANE = Transformer.from_crs(4326, 2968, always_xy=True)
RING_FT = [TO_STATE_PLANE.transform(*TO_GEO.transform(x, y)) for x, y in RING_3857]
RING_PX = [((x-X0_FT)/CELL_FT, (Y0_FT-y)/CELL_FT) for x, y in RING_FT]


def inside(x, y, polygon):
    inside_flag = False
    for i, (x1, y1) in enumerate(polygon):
        x2, y2 = polygon[(i + 1) % len(polygon)]
        if ((y1 > y) != (y2 > y)) and x < (x2-x1) * (y-y1) / (y2-y1) + x1:
            inside_flag = not inside_flag
    return inside_flag


def summary(values_ft):
    arr = np.asarray(values_ft, dtype=float)
    qs = np.quantile(arr, [0, .1, .5, .9, .95, 1])
    return {"n": int(len(arr)), "quantiles_ft_min_p10_median_p90_p95_max": [float(x) for x in qs],
            "quantiles_m_min_p10_median_p90_p95_max": [float(x * 0.3048006096) for x in qs]}

samples = []
for row in range(max(0, int(min(y for _, y in RING_PX))), min(RASTER.shape[0], int(max(y for _, y in RING_PX))+1)):
    for col in range(max(0, int(min(x for x, _ in RING_PX))), min(RASTER.shape[1], int(max(x for x, _ in RING_PX))+1)):
        if inside(col + .5, row + .5, RING_PX):
            x_ft = X0_FT + (col + .5) * CELL_FT
            y_ft = Y0_FT - (row + .5) * CELL_FT
            value_ft = float(RASTER[row, col])
            samples.append({"row": row, "col": col, "x_ftUS": x_ft, "y_ftUS": y_ft, "height_ft": value_ft})
# At the source polygon's notch (Y=1,886,090 ftUS), divide its north crossbar
# from the southern projecting stem; record both rather than assuming they differ.
roof = [s for s in samples if 2.0 <= s["height_ft"] <= 25.0]
main = [s for s in roof if s["y_ftUS"] >= 1886090.0]
wing = [s for s in roof if s["y_ftUS"] < 1886090.0]
# 10-cell buffer around the outline gives a coarse background check. NDHM values
# close to zero are ground-level; trees in this buffer are retained in raw stats.
minc, maxc = int(min(x for x, _ in RING_PX)), int(max(x for x, _ in RING_PX))
minr, maxr = int(min(y for _, y in RING_PX)), int(max(y for _, y in RING_PX))
neighbor = []
for row in range(max(0, minr-10), min(RASTER.shape[0], maxr+11)):
    for col in range(max(0, minc-10), min(RASTER.shape[1], maxc+11)):
        if not inside(col+.5, row+.5, RING_PX):
            neighbor.append(float(RASTER[row, col]))

out = {
 "building_id": "massing_baptist_student_foundation_c3d8114",
 "source": {"title": "Indiana 2017-2019 3DEP LiDAR NDHM", "provider": "Purdue Geospatial Data Science Lab / Indiana Digital Forestry",
  "source_url": "https://giselevationingov.s3.us-east-2.amazonaws.com/ndhmoptimized/statewide/2018/SPW/5ft/in2018_29951885_12_ndhm.tif",
  "tile": "in2018_29951885_12_ndhm.tif", "source_year": 2018, "retrieved": "2026-10-25",
  "tile_query": "audit/baptist_student_foundation/sources/indiana_dem_tile_footprint_query_bsf_2026-10-25.json",
  "query_point_wgs84": [-86.9189, 40.4264], "coverage": "EPSG:2968 tile bounds x 2,995,000–3,000,000 ftUS; y 1,885,000–1,890,000 ftUS; BStF footprint lies inside.",
  "pixel_size_ft": [5,5], "vertical_units": "U.S. survey feet as reported by Purdue GDSL Indiana 3DEP products; values normalized above ground.",
  "tile_georeferencing": "GeoTIFF origin (2,995,000,1,890,000) ftUS; 5-ft pixels; EPSG:2968 NAD83(HARN) Indiana West (ftUS)."},
 "method": {"footprint": "Indiana state lidar-derived building polygon OBJECTID 441814, source EPSG:3857, transformed to EPSG:2968 with pyproj.",
  "sampling": "Raster cell centers inside polygon; no interpolation. Southern stem separated at the source outline's notch y=1,886,090 ftUS.",
  "outlier_handling": "For roof summary only, retained NDHM values 2–25 ft. The low cutoff removes near-ground values; values above 25 ft are treated as likely canopy/contamination. Raw unfiltered samples and nearby values remain included below.",
  "uncertainty": "5-ft cell size; automated footprint and possible tree overhang/pixel mixing. NDHM is a surface-height model, not measured building elevations. Quantiles are approximate roof-surface evidence and cannot individually establish wall-top/eave/ridge heights or floor count."},
 "summary": {"all_inside_outline_raw_ft": summary([s["height_ft"] for s in samples]),
  "roof_cells_filtered_ft_and_m": summary([s["height_ft"] for s in roof]),
  "north_crossbar_filtered_ft_and_m": summary([s["height_ft"] for s in main]),
  "south_stem_filtered_ft_and_m": summary([s["height_ft"] for s in wing]),
  "10_cell_neighbor_values_raw_ft": summary(neighbor)},
 "sample_count": len(samples), "filtered_roof_samples": roof
}
(SOURCES / "indiana_2018_ndhm_bsf_analysis.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(json.dumps(out["summary"], indent=2))
