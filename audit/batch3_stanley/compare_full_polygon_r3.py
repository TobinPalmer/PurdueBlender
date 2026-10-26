"""Full structural foundation polygon comparison to the official Purdue FID 56 ring."""
import json
from pathlib import Path
from shapely.geometry import Polygon

folder = Path(__file__).resolve().parent
asset = json.loads((folder / "asset_foundation_vertices_r3.json").read_text(encoding="utf-8"))
source = json.loads((folder / "source_gis_fid56_r3.json").read_text(encoding="utf-8"))
source_ring = source["feature"]["rings_xy_m"][0]
source_poly = Polygon(source_ring)
low_z = min(v["local_xyz_m"][2] for v in asset["vertices"])
bottom = [v["campus_xy_m"] for v in asset["vertices"] if abs(v["local_xyz_m"][2] - low_z) < 1e-5]
asset_poly = Polygon(bottom)
result = {
    "asset": asset["asset"], "asset_foundation_object": asset["object"],
    "source": source["source"], "source_feature_id": source["feature"]["fid"],
    "source_name": source["feature"]["name"], "source_snapshot_date": source["snapshot_date"],
    "retrieval_date": source["retrieved_for_r3"], "project_coordinate_note": source["crs_note"],
    "transform": asset["coordinate_relation"],
    "source_vertex_count": len(source_poly.exterior.coords) - 1,
    "asset_bottom_vertex_count": len(asset_poly.exterior.coords) - 1,
    "source_area_m2": source_poly.area, "asset_area_m2": asset_poly.area,
    "intersection_over_union": asset_poly.intersection(source_poly).area / asset_poly.union(source_poly).area,
    "symmetric_difference_area_m2": asset_poly.symmetric_difference(source_poly).area,
    "hausdorff_distance_m": asset_poly.hausdorff_distance(source_poly),
    "max_boundary_distance_m": max(asset_poly.boundary.hausdorff_distance(source_poly.boundary), 0.0),
    "asset_valid": asset_poly.is_valid, "source_valid": source_poly.is_valid,
    "height_status": "not assessed by footprint comparison",
    "limits": ["Official outline is campus-map footprint, not a certified survey or wall-line survey.",
               "Project conversion uses the documented approximate local tangent-plane formula.",
               "This comparison checks the lower structural plinth perimeter only; it does not validate facade, roof, or height."]
}
(folder / "full_polygon_comparison_r3.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
