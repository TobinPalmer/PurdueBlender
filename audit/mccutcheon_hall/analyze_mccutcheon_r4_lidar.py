"""Summarize USGS 3DEP classified points over McCutcheon Hall and nearby ground.

Usage: python analyze_mccutcheon_r4_lidar.py <downloaded-LAZ-path>
Requires laspy[lazrs], pyproj, shapely, and numpy.
"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import laspy
import numpy as np
import shapely
from pyproj import CRS, Transformer
from shapely.geometry import shape

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "mccutcheon_hall"
SOURCE = AUDIT / "gis_fid57_source_r4.geojson"
OUTPUT = AUDIT / "mccutcheon_r4_lidar_height.json"
if len(sys.argv) != 2:
    raise SystemExit("Pass the downloaded USGS LAZ filepath as the only argument.")
LAZ = Path(sys.argv[1]).resolve()
if not LAZ.is_file() or LAZ.stat().st_size < 1_000_000:
    raise SystemExit(f"Missing or incomplete LAZ input: {LAZ}")

feature = json.loads(SOURCE.read_text(encoding="utf-8"))["features"][0]
polygon_wgs84 = shape(feature["geometry"])
with laspy.open(LAZ) as reader:
    header = reader.header
    source_crs = header.parse_crs()
    if source_crs is None:
        raise RuntimeError("LAS header has no parseable CRS; do not infer its coordinates.")
    source_crs = CRS.from_user_input(source_crs)
    transformer = Transformer.from_crs(CRS.from_epsg(4326), source_crs, always_xy=True)
    poly_coords = [transformer.transform(lon, lat) for lon, lat in polygon_wgs84.exterior.coords]
    poly = shapely.Polygon(poly_coords)
    unit_factor = source_crs.axis_info[0].unit_conversion_factor or 1.0
    # Buffer 12 m around the mapped building solely to sample nearby class-2 ground.
    near_ground_area = poly.buffer(12.0 / unit_factor).difference(poly)
    poly_minx, poly_miny, poly_maxx, poly_maxy = poly.bounds
    pad = 12.0 / unit_factor
    # This LAS tile has no class-6 points; roof returns are retained as class 1
    # (unclassified).  The source classification histogram is saved in results.
    counts = {"inside_all": 0, "inside_class1_candidate": 0, "outside_ground_class2": 0}
    classification_histogram = {}
    roof_z = []
    ground_z = []
    for points in reader.chunk_iterator(500_000):
        x, y, z = np.asarray(points.x), np.asarray(points.y), np.asarray(points.z)
        cls = np.asarray(points.classification)
        in_extent = (x >= poly_minx-pad) & (x <= poly_maxx+pad) & (y >= poly_miny-pad) & (y <= poly_maxy+pad)
        if not np.any(in_extent):
            continue
        x, y, z, cls = x[in_extent], y[in_extent], z[in_extent], cls[in_extent]
        class_ids, class_counts = np.unique(cls, return_counts=True)
        for class_id, class_count in zip(class_ids, class_counts):
            classification_histogram[str(int(class_id))] = classification_histogram.get(str(int(class_id)), 0) + int(class_count)
        inside = shapely.contains_xy(poly, x, y)
        near_ground = shapely.contains_xy(near_ground_area, x, y)
        counts["inside_all"] += int(inside.sum())
        mask_roof = inside & (cls == 1)
        mask_ground = near_ground & (cls == 2)
        counts["inside_class1_candidate"] += int(mask_roof.sum())
        counts["outside_ground_class2"] += int(mask_ground.sum())
        if np.any(mask_roof):
            roof_z.append(z[mask_roof])
        if np.any(mask_ground):
            ground_z.append(z[mask_ground])

if not roof_z or not ground_z:
    raise RuntimeError(f"Insufficient classified points: {counts}")
roof = np.concatenate(roof_z)
ground = np.concatenate(ground_z)
vertical_unit = "US survey foot"  # USGS product metadata lists this vertical unit.
vertical_to_m = 0.3048006096012192
roof_m = roof * vertical_to_m
ground_m = ground * vertical_to_m
ground_median = float(np.median(ground_m))
high_roof_m = roof_m[roof_m >= ground_median + 15.0]
if not len(high_roof_m):
    raise RuntimeError("No candidate unclassified roof points at least 15 m above nearby ground.")
roof_stats = {str(q): float(np.percentile(high_roof_m, q)) for q in (50, 90, 95, 98, 99, 99.5, 99.9)}
roof_height_bins = {
    str(threshold): int(np.count_nonzero(roof_m >= ground_median + threshold))
    for threshold in (20, 24, 26, 27, 28, 29, 30)
}
result = {
    "source": "USGS National Map 3DEP LiDAR point cloud",
    "product_title": "USGS_LPC_IN_Indiana_Statewide_LiDAR_2017_B17_in2018_29951885_12",
    "download_url": "https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/IN_Indiana_Statewide_LiDAR_2017_B17/IN_Statewide_Opt2_B2_2017/LAZ/USGS_LPC_IN_Indiana_Statewide_LiDAR_2017_B17_in2018_29951885_12.laz",
    "metadata_url": "https://thor-f5.er.usgs.gov/ngtoc/metadata/waf/elevation/lidar_point_cloud/laz/IN_Statewide_Opt2_B2_2017/USGS_LPC_IN_Indiana_Statewide_LiDAR_2017_B17_in2018_29951885_12.xml",
    "acquisition_period": ["2017-03-22", "2018-04-26"],
    "publication_date": "2021-01-18",
    "retrieved_utc": datetime.now(timezone.utc).isoformat(),
    "input_size_bytes": LAZ.stat().st_size,
    "input_sha256": hashlib.sha256(LAZ.read_bytes()).hexdigest(),
    "source_crs_wkt": source_crs.to_wkt(),
    "horizontal_axis_unit": source_crs.axis_info[0].unit_name,
    "vertical_unit_from_las_crs": vertical_unit,
    "vertical_accuracy_in_product_metadata": "N/A",
    "las_classification_histogram_in_building_bbox_plus_buffer": classification_histogram,
    "roof_candidate_count_after_15m_height_filter": int(len(high_roof_m)),
    "roof_return_selection": "Class 1 (unclassified; this tile contains no class-6 building returns), within official FID57 polygon and >=15 m above nearby ground median. Vegetation contamination remains possible.",
    "filter_geometry": "Official GIS FID 57 polygon, transformed from EPSG:4326 using LAS-header CRS; nearby class-2 ground points from a 12 m exterior buffer used as local ground baseline.",
    "classification_counts": counts,
    "ground_class2_z_median_m": ground_median,
    "class1_candidate_z_quantiles_m_after_height_filter": roof_stats,
    "class1_candidate_max_z_m": float(np.max(roof_m)),
    "class1_candidate_count_by_height_above_ground_threshold_m": roof_height_bins,
    "estimated_height_above_nearby_ground_m": {
        k: v-ground_median for k, v in roof_stats.items()
    },
    "limitations": [
        "This LAZ tile contains no class-6 building-class points; roof candidates use class-1 unclassified returns and can include vegetation.",
        "Point cloud is from 2017-2018, not a current as-built survey.",
        "USGS product metadata lists vertical accuracy as N/A; the height is a classified point-cloud estimate, not surveyed elevation.",
        "Roof quantiles may include mechanical equipment; compare several quantiles and imagery before revising the modeled roof.",
        "Ground reference uses nearby class-2 points within a 12 m buffer and may vary with local grading."
    ]
}
OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
