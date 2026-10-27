"""Analyze the public 2018 Tippecanoe COPC tile over Alpha Sigma Phi FID 763."""
import json
from pathlib import Path

import laspy
import numpy as np
from laspy.copc import Bounds, CopcReader
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "audit/alpha_sigma_phi"
TILE = OUT / "sources/in2018_29951885_12.copc.laz"
SOURCE = json.loads((OUT / "sources/arcgis_fid763_feature.json").read_text(encoding="utf-8"))
ring_ll = SOURCE["features"][0]["geometry"]["rings"][0][:-1]
transform = Transformer.from_crs(4326, 2968, always_xy=True)
ring_xy = np.array([transform.transform(lon, lat) for lon, lat in ring_ll])
bounds = Bounds(ring_xy.min(axis=0) - 4.0, ring_xy.max(axis=0) + 4.0)

def inside_polygon(x, y, polygon):
    result = np.zeros(x.shape, dtype=bool)
    j = len(polygon) - 1
    for i, (xi, yi) in enumerate(polygon):
        xj, yj = polygon[j]
        crosses = ((yi > y) != (yj > y)) & (x < (xj - xi) * (y - yi) / ((yj - yi) + 1e-12) + xi)
        result ^= crosses
        j = i
    return result

def distance_to_boundary(x, y, polygon):
    min_sq = np.full(x.shape, np.inf)
    for i, a in enumerate(polygon):
        b = polygon[(i + 1) % len(polygon)]
        vx, vy = b[0] - a[0], b[1] - a[1]
        t = np.clip(((x - a[0]) * vx + (y - a[1]) * vy) / (vx*vx + vy*vy), 0, 1)
        dx, dy = x - (a[0] + t*vx), y - (a[1] + t*vy)
        min_sq = np.minimum(min_sq, dx*dx + dy*dy)
    return np.sqrt(min_sq)

with CopcReader.open(TILE, http_num_threads=8) as reader:
    pts = reader.query(bounds=bounds)
x = np.asarray(pts.x); y = np.asarray(pts.y); z_ft = np.asarray(pts.z)
classification = np.asarray(pts.classification)
in_building = inside_polygon(x, y, ring_xy)
near_edge = distance_to_boundary(x, y, ring_xy) <= 6.0
building_returns = in_building & (classification == 1)
near_ground = near_edge & ~in_building & (classification == 2)
roof_ft = z_ft[building_returns]
roof_xy = np.stack([x[building_returns], y[building_returns]], axis=1)
base_ft = z_ft[near_ground]
if len(roof_ft) == 0 or len(base_ft) == 0:
    raise RuntimeError(f"Insufficient classified points: roof={len(roof_ft)}, base={len(base_ft)}, inside classes={dict(zip(*[a.tolist() for a in np.unique(classification[in_building], return_counts=True)]))}, bbox={bounds.mins.tolist()}..{bounds.maxs.tolist()}")
ground_median_ft = float(np.median(base_ft))
roof_pcts = np.percentile(roof_ft, [5, 50, 95, 99])
fit = np.linalg.lstsq(np.column_stack([roof_xy, np.ones(len(roof_xy))]), roof_ft, rcond=None)[0]
fit_z = np.column_stack([roof_xy, np.ones(len(roof_xy))]) @ fit
fit_r2 = 1.0 - np.sum((roof_ft-fit_z)**2) / np.sum((roof_ft-roof_ft.mean())**2)
result = {
    "source": "Indiana 3DEP 2018 Tippecanoe County LiDAR COPC, tile in2018_29951885_12",
    "source_url": "https://lidar.digitalforestry.org/QL2_3DEP_LiDAR_IN_2017_2019/Tippecanoe_Co_2018_3DEP/Elev18_LAS1.4SPW_IN/copc/in2018_29951885_12.copc.laz",
    "tile_metadata": "sources/indiana_lidar_target_tile_metadata.json",
    "horizontal_crs": "EPSG:2968 NAD83(HARN) / Indiana West (ftUS)",
    "vertical_crs": "NAVD88 height - Geoid12B (ftUS)",
    "classification_method": "COPC query within 4 ft of GIS ring bbox; class 1 unclassified returns inside exact GIS polygon are used only as a roof-surface proxy because no class 6 returns occur within the mapped ring; class 2 ground returns within 6 ft of boundary and outside polygon are the local base estimate",
    "point_counts": {"queried": int(len(pts)), "class_1_inside_ring": int(len(roof_ft)), "class_2_inside_ring": int(np.count_nonzero(in_building & (classification == 2))), "class_6_inside_ring": int(np.count_nonzero(in_building & (classification == 6))), "ground_class_2_nearby": int(len(base_ft))},
    "building_ground_median_ft": round(ground_median_ft, 2),
    "building_roof_returns_ft_percentiles": {str(p): round(float(v), 2) for p, v in zip([5,50,95,99], roof_pcts)},
    "building_height_estimate_m": round((float(np.percentile(roof_ft, 50))-ground_median_ft)*0.3048006096, 2),
    "building_height_upper_estimate_m": round((float(np.percentile(roof_ft, 95))-ground_median_ft)*0.3048006096, 2),
    "roof_z_spread_5_to_95_m": round(float((roof_pcts[2]-roof_pcts[0])*0.3048006096), 2),
    "unclassified_roof_proxy_linear_fit": {"z_ft = ax + by + c": [round(float(v),8) for v in fit], "r_squared": round(float(fit_r2),4), "rmse_ft": round(float(np.sqrt(np.mean((roof_ft-fit_z)**2))),2)},
    "gis_footprint_vertices_transformed_ft": [[round(float(a),2),round(float(b),2)] for a,b in ring_xy],
    "note": "LiDAR-derived approximate roof elevation is not a surveyed wall-height measure; boundary ground sample, roof-edge returns, and 2018 acquisition date contribute uncertainty. It informs roof level but does not resolve facade materials or story arrangement."
}
(OUT / "lidar_height_evidence_2018.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
