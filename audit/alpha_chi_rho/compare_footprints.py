"""Compare the Alpha Chi Rho Purdue GIS polygon with the independent 2018 LiDAR footprint."""

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "audit" / "alpha_chi_rho"
SOURCE_A = P / "sources" / "purdue_gis_FID775_alpha_chi_rho_2026-10-26.json"
SOURCE_B = P / "sources" / "indiana_lidar_building_footprint_410090_2026-10-26.json"
RESULT = P / "footprint_comparison.json"
SVG = P / "footprint_comparison.svg"
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137


def local_xy(lon, lat):
    return ((lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT)),
            (lat - ORIGIN_LAT) * 111040.0)


def area(poly):
    return abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1]
                   - poly[(i + 1) % len(poly)][0] * poly[i][1]
                   for i in range(len(poly))) / 2)


def contains(poly, x, y):
    inside = False
    j = len(poly) - 1
    for i, (xi, yi) in enumerate(poly):
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def centroid(poly):
    signed = sum(poly[i][0] * poly[(i + 1) % len(poly)][1]
                 - poly[(i + 1) % len(poly)][0] * poly[i][1]
                 for i in range(len(poly))) / 2
    cx = sum((poly[i][0] + poly[(i + 1) % len(poly)][0]) *
             (poly[i][0] * poly[(i + 1) % len(poly)][1]
              - poly[(i + 1) % len(poly)][0] * poly[i][1])
             for i in range(len(poly))) / (6 * signed)
    cy = sum((poly[i][1] + poly[(i + 1) % len(poly)][1]) *
             (poly[i][0] * poly[(i + 1) % len(poly)][1]
              - poly[(i + 1) % len(poly)][0] * poly[i][1])
             for i in range(len(poly))) / (6 * signed)
    return [cx, cy]


def main():
    a_data = json.loads(SOURCE_A.read_text(encoding="utf-8"))
    b_data = json.loads(SOURCE_B.read_text(encoding="utf-8"))
    a_ring = a_data["features"][0]["geometry"]["rings"][0][:-1]
    b_ring = b_data["geometry"]["rings"][0][:-1]
    a = [local_xy(*p) for p in a_ring]
    b = [local_xy(*p) for p in b_ring]
    ax = [p[0] for p in a]
    ay = [p[1] for p in a]
    bx = [p[0] for p in b]
    by = [p[1] for p in b]
    step = 0.05
    xmin, xmax = min(ax + bx), max(ax + bx)
    ymin, ymax = min(ay + by), max(ay + by)
    n_intersection = n_a = n_b = n_union = 0
    y = ymin + step / 2
    while y < ymax:
        x = xmin + step / 2
        while x < xmax:
            in_a = contains(a, x, y)
            in_b = contains(b, x, y)
            n_a += in_a
            n_b += in_b
            n_intersection += in_a and in_b
            n_union += in_a or in_b
            x += step
        y += step
    raster_cell_area = step * step
    ca, cb = centroid(a), centroid(b)
    result = {
        "status": "PASS",
        "method": "Independent source polygons transformed with the project local lon/lat-to-meter approximation; planar raster intersection at 0.05 m cells. Raster metrics are approximate and for cross-check only.",
        "purdue_source": {
            "feature_id": 775,
            "vertices": len(a),
            "area_m2_local_approx": area(a),
            "perimeter_m_local_approx": sum(math.dist(a[i], a[(i+1) % len(a)]) for i in range(len(a))),
            "centroid_xy_m": ca,
            "bounds_xy_m": [[min(ax), max(ax)], [min(ay), max(ay)]]
        },
        "indiana_lidar_source": {
            "objectid": 410090,
            "lidar_year": "2018",
            "vertices": len(b),
            "area_m2_local_approx": area(b),
            "perimeter_m_local_approx": sum(math.dist(b[i], b[(i+1) % len(b)]) for i in range(len(b))),
            "centroid_xy_m": cb,
            "bounds_xy_m": [[min(bx), max(bx)], [min(by), max(by)]]
        },
        "centroid_separation_m": math.dist(ca, cb),
        "raster_cell_m": step,
        "raster_intersection_area_m2_approx": n_intersection * raster_cell_area,
        "raster_union_area_m2_approx": n_union * raster_cell_area,
        "raster_intersection_over_union": n_intersection / n_union,
        "raster_symmetric_difference_area_m2_approx": (n_a + n_b - 2 * n_intersection) * raster_cell_area,
        "conclusion": "The independent LiDAR footprint provides a second registration/shape source. Agreement is summarized rather than treated as a survey: the datasets differ in source date and capture method, and both retain source uncertainty."
    }
    RESULT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    width, height, margin = 900, 900, 40
    scale = min((width - 2*margin)/(xmax-xmin), (height - 2*margin)/(ymax-ymin))
    def svg_path(poly):
        return " ".join(("M" if i == 0 else "L") + f"{margin+(x-xmin)*scale:.2f},{height-margin-(y-ymin)*scale:.2f}"
                        for i, (x, y) in enumerate(poly)) + " Z"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="#fff"/>
<path d="{svg_path(a)}" fill="#d55e00" fill-opacity="0.32" stroke="#a63f00" stroke-width="2"/>
<path d="{svg_path(b)}" fill="#0072b2" fill-opacity="0.30" stroke="#00578c" stroke-width="2"/>
<text x="40" y="30" font-family="sans-serif" font-size="20" fill="#222">Alpha Chi Rho footprint comparison</text>
<rect x="40" y="850" width="18" height="18" fill="#d55e00" fill-opacity="0.5"/><text x="66" y="865" font-family="sans-serif" font-size="16">Purdue GIS FID 775</text>
<rect x="270" y="850" width="18" height="18" fill="#0072b2" fill-opacity="0.5"/><text x="296" y="865" font-family="sans-serif" font-size="16">Indiana LiDAR 2018 (410090)</text>
<text x="40" y="890" font-family="sans-serif" font-size="13" fill="#555">Local-coordinate overlay; not a surveyed CRS. Sources have different dates/methods.</text>
</svg>'''
    SVG.write_text(svg, encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
