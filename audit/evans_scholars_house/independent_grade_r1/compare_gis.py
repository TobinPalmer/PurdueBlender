"""Recompute FID 755 footprint agreement from the reopened mesh slab and raw GIS."""
import json
import math
from pathlib import Path

from shapely.geometry import Polygon

ROOT = Path(__file__).resolve().parents[3]
probe = json.loads((ROOT / "audit/evans_scholars_house/independent_grade_r1/geometry_probe.json").read_text())
feature = json.loads((ROOT / "audit/evans_scholars_house/fid755_arcgis.geojson").read_text())["features"][0]
ring = feature["geometry"]["coordinates"][0]
lat0, lon0 = 40.4274, -86.9137
projected = [((lon - lon0) * 111412.84 * math.cos(math.radians(lat0)), (lat - lat0) * 111040.0)
             for lon, lat, *_ in ring]
source_polygon_projected = Polygon(projected)
center = source_polygon_projected.centroid
source = Polygon([(x - center.x, y - center.y) for x, y in projected])
mesh_points = probe["slab_vertices_local_xy"]
unique = []
for point in mesh_points:
    if not any((point[0] - prior[0]) ** 2 + (point[1] - prior[1]) ** 2 < 1e-9 for prior in unique):
        unique.append(point)
model = Polygon(unique)
iou = source.intersection(model).area / source.union(model).area
result = {
    "method": "Reopened asset's GIS footprint foundation slab XY vertices compared to saved Purdue FID 755 exterior ring transformed from EPSG:4326 with the documented project-local conversion; both centered at the source polygon centroid.",
    "qualification": "The source polygon was used to originate the asset. This independent parse/reopen check verifies that its footprint and transform survived serialization; it is not independent proof that GIS wall lines are surveyed truth.",
    "source_feature_id": feature["properties"].get("FID"),
    "source_address": feature["properties"].get("ADDRESS"),
    "source_name": feature["properties"].get("BUILDING_N"),
    "source_crs": "EPSG:4326 response geometry; transformed using project approximation to local XY meters",
    "source_vertex_count": len(source.exterior.coords) - 1,
    "model_slab_unique_vertex_count": len(unique),
    "source_area_m2": source.area,
    "model_area_m2": model.area,
    "intersection_over_union": iou,
    "symmetric_boundary_hausdorff_m": source.boundary.hausdorff_distance(model.boundary),
    "source_bounds_m": list(source.bounds),
    "model_bounds_m": list(model.bounds),
}
out = ROOT / "audit/evans_scholars_house/independent_grade_r1/gis_comparison.json"
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
