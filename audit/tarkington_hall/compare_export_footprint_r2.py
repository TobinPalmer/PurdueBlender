"""Recompute shell-to-GIS footprint using only named export-collection objects."""
from __future__ import annotations

import json
import math
from pathlib import Path

from shapely.geometry import MultiPoint, Polygon
from shapely.ops import unary_union

AUDIT = Path(__file__).resolve().parent
gis_feature = json.loads((AUDIT / "gis_feature_662.json").read_text(encoding="utf-8"))["feature"]
all_shells = json.loads((AUDIT / "shell_vertices_r2.json").read_text(encoding="utf-8"))["objects"]
membership = json.loads((AUDIT / "independent_membership_r2.json").read_text(encoding="utf-8"))
origin_x, origin_y = (-591.6124877929688, 348.0)
lon0, lat0 = (-86.9137, 40.4274)
xscale = 111412.84 * math.cos(math.radians(lat0))
yscale = 111040.0
rings = gis_feature["geometry"]["rings"]
source_rings = [
    [((lon - lon0) * xscale - origin_x, (lat - lat0) * yscale - origin_y) for lon, lat in ring]
    for ring in rings
]
gis = Polygon(source_rings[0], source_rings[1:])
export_names = set(membership["export_object_names"])
parts = [
    (record["name"], MultiPoint(record["vertices_xy"]).convex_hull)
    for record in all_shells
    if record["name"] in export_names
]
parts = [(name, geom) for name, geom in parts if geom.geom_type == "Polygon" and geom.area > 0]
model = unary_union([geom for _, geom in parts])
intersection = gis.intersection(model).area
union = gis.union(model).area


def samples(line, step=0.25):
    points = []
    lines = line.geoms if hasattr(line, "geoms") else [line]
    for segment in lines:
        count = max(1, int(math.ceil(segment.length / step)))
        points.extend(segment.interpolate(i / count, normalized=True) for i in range(count + 1))
    return points


source_points = samples(gis.boundary)
model_points = samples(model.boundary)
source_to_model = [point.distance(model.boundary) for point in source_points]
model_to_source = [point.distance(gis.boundary) for point in model_points]
residuals = source_to_model + model_to_source
source_bounds = gis.bounds
model_bounds = model.bounds
result = {
    "asset_sha256": membership["asset_sha256"],
    "feature_id": int(gis_feature["attributes"]["FID"]),
    "building_code": gis_feature["attributes"]["BLDG_ABBR"],
    "shell_selection": "Only named structural-shell objects whose object names belong to Asset_tarkington_hall",
    "shell_object_names": [name for name, _ in parts],
    "shell_object_count": len(parts),
    "source_polygon_area_m2": gis.area,
    "export_shell_union_area_m2": model.area,
    "intersection_area_m2": intersection,
    "union_area_m2": union,
    "export_shell_iou": intersection / union if union else 0,
    "mean_symmetric_boundary_residual_m": sum(residuals) / len(residuals),
    "p95_symmetric_boundary_residual_m": sorted(residuals)[int(0.95 * (len(residuals) - 1))],
    "symmetric_boundary_hausdorff_m": gis.boundary.hausdorff_distance(model.boundary),
    "centroid_delta_m": [model.centroid.x - gis.centroid.x, model.centroid.y - gis.centroid.y],
    "source_bounds_local_xy_m": [[source_bounds[0], source_bounds[2]], [source_bounds[1], source_bounds[3]]],
    "export_shell_bounds_local_xy_m": [[model_bounds[0], model_bounds[2]], [model_bounds[1], model_bounds[3]]],
    "excluded_shells": [record["name"] for record in all_shells if record["name"] not in export_names],
    "limitations": [
        "The Purdue GIS outline is not documented as a surveyed wall-face polygon.",
        "The official 2023 orthophoto is a roof-edge proxy; roof overhangs can differ from wall faces.",
        "Shell object convex hulls can bridge local setbacks and openings.",
        "The local geographic conversion is approximate, not a surveyed projection.",
    ],
}
(AUDIT / "footprint_export_only_r2.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
