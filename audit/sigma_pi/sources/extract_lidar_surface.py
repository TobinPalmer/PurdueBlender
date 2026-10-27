"""Extract and summarize the 2018 QL2 surface returns over Sigma Pi FID 776.

Reproduce with Python plus laspy/lazrs, pyproj, shapely and numpy:
    python extract_lidar_surface.py <path-to-in2018_29951885_12.copc.laz>

The COPC tile remains an external source. This script writes a compact point
snapshot and summary beside itself. LAS source XY/Z/classification values are
retained; derived local XY and height-above-ground values are included for the
Blender builder. Class 1 is unclassified, so returns are not asserted to be
building-classified roof points.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from datetime import date
from pathlib import Path

import laspy
import numpy as np
from pyproj import Transformer
from shapely.geometry import Point, Polygon


HERE = Path(__file__).resolve().parent
GIS = HERE / "purdue_gis_fid776_sigma_pi_2026-10-26.json"
OUTPUT_CSV = HERE / "sigma_pi_lidar_fid776_returns.csv"
OUTPUT_JSON = HERE / "sigma_pi_lidar_surface_analysis.json"
TILE_URL = (
    "https://lidar.digitalforestry.org/QL2_3DEP_LiDAR_IN_2017_2019/"
    "Tippecanoe_Co_2018_3DEP/Elev18_LAS1.4SPW_IN/copc/"
    "in2018_29951885_12.copc.laz"
)
EPSG_LAS = 2968
GROUND_BUFFER_FT = 32.80839895  # 10 m in US survey feet
SURFACE_FILTER_FT = 650.0
FT_TO_M = 0.3048006096012192


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: extract_lidar_surface.py <COPC-LAZ-path>")
    laz_path = Path(sys.argv[1]).resolve()
    feature = json.loads(GIS.read_text(encoding="utf-8"))
    ring_ll = feature["geometry"]["rings"][0]
    to_las = Transformer.from_crs(4326, EPSG_LAS, always_xy=True)
    ring_xy = [to_las.transform(lon, lat) for lon, lat in ring_ll]
    footprint = Polygon(ring_xy)
    to_ll = Transformer.from_crs(EPSG_LAS, 4326, always_xy=True)
    origin_lon, origin_lat = -86.9137, 40.4274
    lon_m = 111412.84 * math.cos(math.radians(origin_lat))
    lat_m = 111040.0

    with laspy.open(laz_path) as reader:
        hdr = reader.header
        raw_crs = hdr.parse_crs()
        all_points = []
        class2_ground = []
        for chunk in reader.chunk_iterator(1_000_000):
            x = np.asarray(chunk.x)
            y = np.asarray(chunk.y)
            z = np.asarray(chunk.z)
            cls = np.asarray(chunk.classification)
            intensity = np.asarray(chunk.intensity)
            return_number = np.asarray(chunk.return_number)
            # Use a quick bbox first, then exact ring membership.
            minx, miny, maxx, maxy = footprint.bounds
            in_bbox = (x >= minx - GROUND_BUFFER_FT) & (x <= maxx + GROUND_BUFFER_FT) & (
                y >= miny - GROUND_BUFFER_FT
            ) & (y <= maxy + GROUND_BUFFER_FT)
            if not np.any(in_bbox):
                continue
            for idx in np.flatnonzero(in_bbox):
                px, py, pz = float(x[idx]), float(y[idx]), float(z[idx])
                pclass = int(cls[idx])
                inside = footprint.covers(Point(px, py))
                if inside:
                    all_points.append((px, py, pz, pclass, int(intensity[idx]), int(return_number[idx])))
                elif pclass == 2 and footprint.distance(Point(px, py)) <= GROUND_BUFFER_FT:
                    class2_ground.append(pz)

    if not class2_ground:
        raise RuntimeError("No nearby class-2 ground returns found")
    ground_median_ft = float(np.median(class2_ground))
    pts = np.asarray(all_points, dtype=np.float64)
    if pts.size == 0:
        raise RuntimeError("No returns inside FID 776 footprint")
    local_rows = []
    for x, y, z, cls, intensity, ret in pts:
        lon, lat = to_ll.transform(float(x), float(y))
        local_x = (lon - origin_lon) * lon_m
        local_y = (lat - origin_lat) * lat_m
        local_z = (float(z) - ground_median_ft) * FT_TO_M
        local_rows.append((x, y, z, int(cls), int(intensity), int(ret), local_x, local_y, local_z))

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "source_x_usft", "source_y_usft", "source_z_navd88_usft", "classification",
            "intensity", "return_number", "project_local_x_m", "project_local_y_m",
            "height_above_nearby_ground_m",
        ])
        writer.writerows(local_rows)

    arr = np.asarray(local_rows, dtype=np.float64)
    cls_counts = {str(int(c)): int((pts[:, 3] == c).sum()) for c in np.unique(pts[:, 3])}
    hi = pts[:, 2] >= SURFACE_FILTER_FT
    hi_z = pts[hi, 2]
    percentiles = {f"p{p}": float(np.percentile(hi_z, p)) for p in (10, 25, 50, 75, 90)}
    analysis = {
        "building_id": "massing_house_301836568_0fbca0e",
        "retrieved_date": str(date.today()),
        "source": {
            "provider": "Indiana Statewide Elevation Data / Purdue GIS Data Service Lab",
            "url": TILE_URL,
            "tile": laz_path.name,
            "sha256": sha256(laz_path),
            "bytes": laz_path.stat().st_size,
            "header_point_count": int(hdr.point_count),
            "header_crs": str(raw_crs),
            "header_scales": [float(v) for v in hdr.scales],
            "header_offsets": [float(v) for v in hdr.offsets],
            "acquisition_period": "2018 Tippecanoe County QL2 LiDAR (tile name / distribution metadata)",
            "vertical_datum": "NAVD88 height, US survey feet",
            "horizontal_crs": "EPSG:2968 NAD83(HARN) / Indiana West (ftUS)",
        },
        "footprint": {
            "source": GIS.name,
            "source_feature_id": 776,
            "source_crs": "EPSG:4326; projected to EPSG:2968 for exact membership",
            "ring_vertices": len(ring_ll) - 1,
            "project_local_xy": "matches modular/AGENTS.md local geographic approximation; origin -86.9137, 40.4274",
        },
        "method": {
            "returns_inside_footprint": "LAS returns whose XY are covered by the exact transformed GIS ring",
            "ground_sample": "Class 2 returns outside the ring within 10 m; median used as local datum",
            "roof_candidate_filter": f"Class 1 returns at or above {SURFACE_FILTER_FT:g} ft NAVD88. Threshold is an analysis filter (>8.3 m above ground median), not a semantic roof classification.",
            "height_formula": "(source_z_NAVD88_usft - nearby_class2_ground_median_usft) * 0.3048006096012192",
            "roof_surface": "Filtered unclassified surface returns indicate high central bands and depressed perimeter; vegetation and other objects cannot be fully excluded.",
        },
        "counts": {
            "returns_inside": int(len(pts)),
            "classification_counts": cls_counts,
            "nearby_class2_ground_returns": int(len(class2_ground)),
            "surface_filter_returns": int(hi.sum()),
        },
        "statistics": {
            "nearby_ground_class2_median_navd88_usft": ground_median_ft,
            "class1_inside_z_navd88_usft": {
                f"p{p}": float(np.percentile(pts[pts[:, 3] == 1, 2], p))
                for p in (10, 50, 90, 100)
            },
            "filtered_surface_navd88_usft": percentiles,
            "filtered_surface_height_above_ground_m": {
                f"p{p}": float((np.percentile(hi_z, p) - ground_median_ft) * FT_TO_M)
                for p in (10, 25, 50, 75, 90, 100)
            },
        },
        "snapshot": OUTPUT_CSV.name,
        "snapshot_sha256": sha256(OUTPUT_CSV),
        "limits": [
            "No class-6 building returns were present within the ring; class 1 means unclassified.",
            "The LiDAR supports surface heights and roof articulation, but does not independently identify wall lines, floors, or stories.",
            "LiDAR point density, return classification, roof-edge trees, and local ground sample introduce uncertainty.",
        ],
    }
    OUTPUT_JSON.write_text(json.dumps(analysis, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"csv": str(OUTPUT_CSV), "summary": str(OUTPUT_JSON), **analysis["counts"], **analysis["statistics"]}, indent=2))


if __name__ == "__main__":
    main()
