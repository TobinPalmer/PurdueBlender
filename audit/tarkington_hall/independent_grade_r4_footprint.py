"""Independently compare the frozen R4 shell to Purdue GIS FID 662."""
from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import MultiPoint, Polygon
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "audit" / "tarkington_hall"
candidate = json.loads((OUT / "independent_grade_r4_shell_vertices.json").read_text(encoding="utf-8"))
if candidate["asset_sha256"] != "b844a77e35ad44bf722ea0432ed40dc47a6b01fff24c095cbabf68e760f87065":
    raise RuntimeError("Fresh Blender extraction is not the frozen R4 SHA")
feature = json.loads((OUT / "gis_feature_662.json").read_text(encoding="utf-8"))["feature"]
rings = feature["geometry"]["rings"]
lon0, lat0 = -86.9137, 40.4274
xscale = 111412.84 * math.cos(math.radians(lat0))
yscale = 111040.0
campus_origin = (-591.6124877929688, 348.0)

def to_model_local(ring):
    return [
        ((float(lon) - lon0) * xscale - campus_origin[0],
         (float(lat) - lat0) * yscale - campus_origin[1])
        for lon, lat in ring
    ]

source = Polygon(to_model_local(rings[0]), [to_model_local(ring) for ring in rings[1:]])
parts = []
for record in candidate["objects"]:
    hull = MultiPoint(record["vertices_xy"]).convex_hull
    if hull.geom_type == "Polygon" and hull.area > 0:
        parts.append(hull)
model = unary_union(parts)
intersection = source.intersection(model).area
union = source.union(model).area

def sample_boundary(geom, step=0.25):
    lines = list(geom.geoms) if hasattr(geom, "geoms") else [geom]
    samples = []
    for line in lines:
        n = max(1, int(math.ceil(line.length / step)))
        samples.extend(line.interpolate(i / n, normalized=True) for i in range(n + 1))
    return samples

source_samples = sample_boundary(source.boundary)
model_samples = sample_boundary(model.boundary)
source_to_model = [point.distance(model.boundary) for point in source_samples]
model_to_source = [point.distance(source.boundary) for point in model_samples]
all_residuals = sorted(source_to_model + model_to_source)
p95 = all_residuals[min(len(all_residuals) - 1, int(0.95 * (len(all_residuals) - 1)))]
metrics = {
    "building": "Tarkington Hall",
    "candidate_sha256": candidate["asset_sha256"],
    "source_provider": "Purdue University ArcGIS BuildingShapesZip4 FeatureServer layer 0",
    "feature_id": int(feature["attributes"]["FID"]),
    "building_code": feature["attributes"]["BLDG_ABBR"],
    "source_crs": "EPSG:4326",
    "source_retrieved_date": "2026-10-22 snapshot; packed 2026-10-25",
    "source_to_model_transform": {
        "longitude_origin": lon0,
        "latitude_origin": lat0,
        "x_scale_m_per_degree": xscale,
        "y_scale_m_per_degree": yscale,
        "subtract_master_placement_origin_m": list(campus_origin),
        "limitation": "Local geographic approximation, not survey-grade CRS.",
    },
    "shell_selection": candidate["selection_method"],
    "shell_object_count": len(candidate["objects"]),
    "source_polygon_area_m2": source.area,
    "model_shell_union_area_m2": model.area,
    "intersection_area_m2": intersection,
    "union_area_m2": union,
    "polygon_iou": intersection / union if union else 0.0,
    "symmetric_mean_boundary_residual_m": sum(all_residuals) / len(all_residuals),
    "symmetric_p95_boundary_residual_m": p95,
    "symmetric_hausdorff_m": source.boundary.hausdorff_distance(model.boundary),
    "centroid_offset_xy_m": [model.centroid.x - source.centroid.x, model.centroid.y - source.centroid.y],
    "source_bounds_model_local_m": [[source.bounds[0], source.bounds[2]], [source.bounds[1], source.bounds[3]]],
    "model_bounds_local_m": [[model.bounds[0], model.bounds[2]], [model.bounds[1], model.bounds[3]]],
    "limitations": [
        "GIS outline has no documented wall-face survey semantics; 2023 orthophoto supports it as roof/edge proxy.",
        "Model shell union uses convex hulls per named structural shell; local setbacks and openings may bridge.",
        "The Hausdorff maximum is an isolated extreme and should be read with mean/P95 and visual overlay.",
    ],
}
(OUT / "independent_grade_r4_footprint.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

# Independent vector overlay for visual review.
width, height = 1400, 1100
minx, miny, maxx, maxy = source.union(model).bounds
pad = max((maxx - minx) * 0.06, 2.0)
minx, maxx, miny, maxy = minx - pad, maxx + pad, miny - pad, maxy + pad
scale = min((width - 140) / (maxx - minx), (height - 180) / (maxy - miny))
def pixel(point):
    return (int(70 + (point[0] - minx) * scale), int(height - 90 - (point[1] - miny) * scale))

image = Image.new("RGB", (width, height), (248, 249, 251))
draw = ImageDraw.Draw(image, "RGBA")
def draw_poly(poly, fill, outline):
    draw.polygon([pixel(point) for point in poly.exterior.coords], fill=fill, outline=outline)
    for hole in poly.interiors:
        draw.polygon([pixel(point) for point in hole.coords], fill=(248, 249, 251, 255), outline=outline)

draw_poly(source, (197, 54, 68, 70), (197, 54, 68, 255))
geoms = list(model.geoms) if hasattr(model, "geoms") else [model]
for geom in geoms:
    if geom.geom_type == "Polygon":
        draw_poly(geom, (23, 110, 171, 65), (23, 110, 171, 255))
try:
    font = ImageFont.truetype("arial.ttf", 25)
    small = ImageFont.truetype("arial.ttf", 19)
except OSError:
    font = small = ImageFont.load_default()
draw.text((70, 20), "Independent Tarkington Hall R4 footprint check", font=font, fill=(25, 35, 45, 255))
draw.text((70, 55), f"IoU {metrics['polygon_iou']:.3f} | mean {metrics['symmetric_mean_boundary_residual_m']:.2f} m | P95 {p95:.2f} m | FID 662", font=small, fill=(45, 55, 65, 255))
draw.line((70, height - 50, 155, height - 50), fill=(197, 54, 68, 255), width=5)
draw.text((165, height - 60), "Purdue GIS", font=small, fill=(45, 55, 65, 255))
draw.line((330, height - 50, 415, height - 50), fill=(23, 110, 171, 255), width=5)
draw.text((425, height - 60), "R4 structural shell", font=small, fill=(45, 55, 65, 255))
image.save(OUT / "independent_grade_r4_footprint_overlay.png")
print(json.dumps(metrics, indent=2))
