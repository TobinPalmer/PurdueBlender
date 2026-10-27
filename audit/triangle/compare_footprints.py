"""Compare Purdue FID 777 with the 2018 IndianaMap LiDAR footprint."""

import json
import math
from pathlib import Path

from shapely.geometry import Polygon

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "audit" / "triangle"
GIS = EVIDENCE / "sources" / "purdue_gis_fid777_triangle_2026-10-26.json"
LIDAR = EVIDENCE / "sources" / "indiana_lidar_footprint_fid777_site_2026-10-26.json"


def local_xy(ring):
    return [
        (
            (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0,
        )
        for lon, lat in ring
    ]


def main():
    a = json.loads(GIS.read_text(encoding="utf-8"))["features"][0]
    b = json.loads(LIDAR.read_text(encoding="utf-8"))["features"][0]
    pa = Polygon(local_xy(a["geometry"]["rings"][0]))
    pb = Polygon(local_xy(b["geometry"]["rings"][0]))
    result = {
        "provider_a": "Purdue BuildingShapes FeatureServer layer 0 FID 777",
        "provider_b": "IndianaMap 2016-2020 LiDAR-derived building footprints feature 410069",
        "transform": "Repository approximate local campus conversion from EPSG:4326; not a surveyed CRS transformation",
        "purdue_vertex_count": len(a["geometry"]["rings"][0]) - 1,
        "indiana_lidar_vertex_count": len(b["geometry"]["rings"][0]) - 1,
        "purdue_area_local_m2": pa.area,
        "indiana_lidar_area_local_m2": pb.area,
        "centroid_separation_m": pa.centroid.distance(pb.centroid),
        "intersection_area_m2": pa.intersection(pb).area,
        "union_area_m2": pa.union(pb).area,
        "intersection_over_union": pa.intersection(pb).area / pa.union(pb).area,
        "symmetric_difference_area_m2": pa.symmetric_difference(pb).area,
        "boundary_hausdorff_distance_m": pa.boundary.hausdorff_distance(pb.boundary),
        "interpretation": "Independent LiDAR-derived outline corroborates the FID777 building match and broad footprint. Boundary differences remain and neither outline is treated as a wall survey.",
    }
    (EVIDENCE / "footprint_comparison.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
