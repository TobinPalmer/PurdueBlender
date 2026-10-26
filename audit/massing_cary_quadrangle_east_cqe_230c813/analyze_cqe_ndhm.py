"""Sample the CQE GIS outline against the 2018 Indiana 3DEP NDHM tile.

The NDHM gives approximate above-ground surface heights, not surveyed roof
elevations. It is used only as corroboration for the roof-height range.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import tifffile
from pyproj import Transformer

HERE = Path(__file__).resolve().parent
SOURCES = HERE / "sources"
footprint = json.loads((SOURCES / "purdue_building_shapes_fid639_cqe_2026-10-25.geojson").read_text(encoding="utf-8"))
ring = footprint["features"][0]["geometry"]["coordinates"][0]
raster_path = SOURCES / "in2018_29951885_12_ndhm.tif"
raster = tifffile.imread(raster_path)
X0_FT, Y0_FT, CELL_FT = 2995000.0, 1890000.0, 5.0
to_sp = Transformer.from_crs(4326, 2968, always_xy=True)
ring_ft = [to_sp.transform(lon, lat) for lon, lat in ring]
ring_px = [((x - X0_FT) / CELL_FT, (Y0_FT - y) / CELL_FT) for x, y in ring_ft]


def inside(x, y, poly):
    hit = False
    for i, (x1, y1) in enumerate(poly):
        x2, y2 = poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            hit = not hit
    return hit


def stats(vals):
    a = np.asarray(vals, dtype=float)
    if not len(a):
        return {"n": 0, "quantile_order": ["min", "p10", "p25", "median", "p75", "p90", "p95", "max"],
                "quantiles_ftUS": [], "quantiles_m": []}
    q = np.quantile(a, [0, .1, .25, .5, .75, .9, .95, 1])
    return {
        "n": int(len(a)),
        "quantile_order": ["min", "p10", "p25", "median", "p75", "p90", "p95", "max"],
        "quantiles_ftUS": [float(v) for v in q],
        "quantiles_m": [float(v * 0.3048006096) for v in q],
    }


minc, maxc = int(min(x for x, _ in ring_px)), int(max(x for x, _ in ring_px))
minr, maxr = int(min(y for _, y in ring_px)), int(max(y for _, y in ring_px))
cells = []
for row in range(max(0, minr), min(raster.shape[0], maxr + 1)):
    for col in range(max(0, minc), min(raster.shape[1], maxc + 1)):
        if inside(col + .5, row + .5, ring_px):
            h = float(raster[row, col])
            cells.append({"row": row, "col": col, "x_ftUS": X0_FT + (col + .5) * CELL_FT,
                          "y_ftUS": Y0_FT - (row + .5) * CELL_FT, "height_ftUS": h})

# Preserve all samples; 25–65 ft is a transparent likely-roof screen selected
# from the strong separation between near-ground neighborhood cells and the
# interior distribution. It remains a screen, not proof every pixel is roof.
roof = [c for c in cells if 25.0 <= c["height_ftUS"] <= 65.0]
neighbor = []
for row in range(max(0, minr - 10), min(raster.shape[0], maxr + 11)):
    for col in range(max(0, minc - 10), min(raster.shape[1], maxc + 11)):
        if not inside(col + .5, row + .5, ring_px):
            neighbor.append(float(raster[row, col]))

out = {
    "building_id": "massing_cary_quadrangle_east_cqe_230c813",
    "source": {
        "provider": "Purdue Geospatial Data Science Lab / Indiana Digital Forestry",
        "title": "Indiana 2017–2019 3DEP LiDAR Normalized Digital Height Model",
        "url": "https://giselevationingov.s3.us-east-2.amazonaws.com/ndhmoptimized/statewide/2018/SPW/5ft/in2018_29951885_12_ndhm.tif",
        "metadata_snapshot": "sources/indiana_2018_ndhm_source_metadata.json",
        "source_snapshot": "sources/in2018_29951885_12_ndhm.tif",
        "collection_year": 2018,
        "retrieved_local_date": "2026-10-26",
        "crs": "EPSG:2968, NAD83(HARN) / Indiana West (ftUS)",
        "pixel_size": "5 ft x 5 ft",
        "tile_georeferencing": "Upper-left (2,995,000, 1,890,000) ftUS; rows increase south, columns increase east.",
        "source_sha256": hashlib.sha256(raster_path.read_bytes()).hexdigest(),
        "tile_bounds_ftUS": {"x": [2995000, 3000000], "y": [1885000, 1890000]},
    },
    "footprint": {
        "provider": "Purdue BuildingShapesZip4 FeatureServer/0",
        "feature_id": 639,
        "identity": "BLDG_ABBR=CQE; Franklin Levering Cary Quadrangle (East)",
        "snapshot": "sources/purdue_building_shapes_fid639_cqe_2026-10-25.geojson",
        "input_crs": "EPSG:4326",
        "transform": "EPSG:4326 to EPSG:2968 with pyproj; cell center samples tested inside projected polygon.",
        "projected_ring_bounds_ftUS": [[float(min(x for x, _ in ring_ft)), float(min(y for _, y in ring_ft))],
                                        [float(max(x for x, _ in ring_ft)), float(max(y for _, y in ring_ft))]],
    },
    "method": {
        "sampling": "Raster cell centers inside the official CQE polygon; nearest cell value, no interpolation.",
        "likely_roof_screen": "25–65 ftUS above ground, an analysis choice informed by the neighborhood distribution to exclude near-ground/mixed edge cells and extreme values; raw values are preserved below.",
        "neighbor_check": "All raster cells outside the polygon and inside a 10-cell (50 ft) bounding-box buffer.",
        "uncertainty": "Five-foot cells mix roof, ground, and overhanging canopy near edges. The raster is a normalized surface model, not a measured elevation survey. Screening and polygon geometry affect statistics; height quantiles support only an approximate surface-height range, not floor count or eave/ridge height individually.",
    },
    "coverage_check": {
        "raster_shape_rows_cols": [int(raster.shape[0]), int(raster.shape[1])],
        "polygon_inside_tile": bool(min(x for x, _ in ring_px) >= 0 and min(y for _, y in ring_px) >= 0 and
                                     max(x for x, _ in ring_px) < raster.shape[1] and max(y for _, y in ring_px) < raster.shape[0]),
    },
    "summary": {
        "all_inside_polygon_raw": stats([c["height_ftUS"] for c in cells]),
        "screened_likely_roof": stats([c["height_ftUS"] for c in roof]),
        "10_cell_neighbor_raw": stats(neighbor),
    },
    "sample_count": len(cells),
    "screened_roof_samples": roof,
    "raw_inside_samples": cells,
}
(HERE / "cqe_ndhm_analysis.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(json.dumps({"coverage_check": out["coverage_check"], "summary": out["summary"]}, indent=2))
