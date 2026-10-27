"""Create a triangulated roof-height surface from the retained QL2 return ROI.

Run after extract_lidar_surface.py. The grid is an IDW interpolation of nearby
unclassified high returns; it is a visualized LiDAR surface estimate, not a
surveyed roof or wall model. Blender builder reads the resulting JSON mesh.
"""

import csv
import json
import math
from pathlib import Path

import numpy as np
from shapely import constrained_delaunay_triangles
from shapely.geometry import Point, Polygon, box


HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "sigma_pi_lidar_fid776_returns.csv"
GIS_PATH = HERE / "purdue_gis_fid776_sigma_pi_2026-10-26.json"
OUT_PATH = HERE / "sigma_pi_lidar_roof_mesh.json"
ORIGIN_LON, ORIGIN_LAT = -86.9137, 40.4274
SURFACE_FILTER_FT = 650.0
GROUND_MEDIAN_FT = 622.83
FT_TO_M = 0.3048006096012192


def local_ring():
    data = json.loads(GIS_PATH.read_text(encoding="utf-8"))
    ring = data["geometry"]["rings"][0]
    lon_scale = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
    return [((lon - ORIGIN_LON) * lon_scale, (lat - ORIGIN_LAT) * 111040.0) for lon, lat in ring]


def main():
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    all_xy = np.asarray([[float(r["project_local_x_m"]), float(r["project_local_y_m"])] for r in rows])
    source_z = np.asarray([float(r["source_z_navd88_usft"]) for r in rows])
    classifications = np.asarray([int(r["classification"]) for r in rows])
    keep = (classifications == 1) & (source_z >= SURFACE_FILTER_FT)
    sample_xy = all_xy[keep]
    sample_z = (source_z[keep] - GROUND_MEDIAN_FT) * FT_TO_M
    clip_low, clip_high = np.percentile(sample_z, (5, 95))
    sample_z = np.clip(sample_z, clip_low, clip_high)
    polygon = Polygon(local_ring())

    # Clip a 0.9 m grid of cells to the exact GIS ring, then constrained-
    # triangulate each clipped cell. This preserves the concave footprint with
    # no gaps while avoiding a false claim that the sparse point cloud is dense.
    minx, miny, maxx, maxy = polygon.bounds
    step = 0.9
    vertices = []
    faces = []
    index = {}

    def vertex_for(x, y):
        key = (round(float(x), 8), round(float(y), 8))
        if key in index:
            return index[key]
        d2 = np.sum((sample_xy - np.array([x, y])) ** 2, axis=1)
        n = min(16, len(d2))
        nearest = np.argpartition(d2, n - 1)[:n]
        # Median-based local interpolation damps isolated extreme returns;
        # inverse distance weights preserve the nearby ridge/valley patterns.
        if np.min(d2[nearest]) < 0.04:
            z = float(sample_z[nearest[np.argmin(d2[nearest])]])
        else:
            weights = 1.0 / np.sqrt(np.maximum(d2[nearest], 0.5))
            order = np.argsort(sample_z[nearest])
            zs, ws = sample_z[nearest][order], weights[order]
            z = float(np.average(zs, weights=ws))
        index[key] = len(vertices)
        vertices.append([key[0], key[1], z])
        return index[key]

    x0 = minx
    while x0 < maxx:
        x1 = min(x0 + step, maxx)
        y0 = miny
        while y0 < maxy:
            y1 = min(y0 + step, maxy)
            clipped = box(x0, y0, x1, y1).intersection(polygon)
            if not clipped.is_empty:
                geoms = list(clipped.geoms) if hasattr(clipped, "geoms") else [clipped]
                for part in geoms:
                    if part.geom_type != "Polygon" or part.area < 1e-8:
                        continue
                    for tri in constrained_delaunay_triangles(part).geoms:
                        if tri.geom_type != "Polygon" or tri.area < 1e-8:
                            continue
                        ids = [vertex_for(x, y) for x, y in list(tri.exterior.coords)[:3]]
                        faces.append(ids)
            y0 = y1
        x0 = x1

    result = {
        "method": "Constrained triangulation of 0.9 m grid cells clipped to the exact GIS ring; IDW of 16 nearest class-1 returns >=650 ft NAVD88 with candidate return heights clipped to their 5th-95th percentile range to reduce isolated returns; surface estimates relative to nearby class-2 ground median 622.83 ft.",
        "analysis_source": "sigma_pi_lidar_surface_analysis.json",
        "source_snapshot": CSV_PATH.name,
        "source_return_filter": "classification == 1 and source_z_navd88_usft >= 650",
        "source_return_count": int(keep.sum()),
        "source_return_height_clip_m_above_ground": [float(clip_low), float(clip_high)],
        "ground_median_navd88_usft": GROUND_MEDIAN_FT,
        "grid_step_m": step,
        "vertices": vertices,
        "faces": [list(f) for f in faces],
        "limits": "Unclassified returns may include vegetation or other objects. This triangulated surface is a roof articulation guide from 2018 LiDAR, not a measured wall line, floor count, or surveyed roof mesh.",
    }
    OUT_PATH.write_text(json.dumps(result, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(OUT_PATH), "source_return_count": int(keep.sum()), "vertices": len(vertices), "faces": len(faces), "z_min_m": min(v[2] for v in vertices), "z_max_m": max(v[2] for v in vertices)}, indent=2))


if __name__ == "__main__":
    main()
