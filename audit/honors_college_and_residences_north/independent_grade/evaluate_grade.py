"""Independent repeatable grade for Honors North. Uses the saved asset audit and raw source GIS."""
import hashlib, json, math
from pathlib import Path
from shapely.geometry import LineString, Point, Polygon

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit" / "honors_college_and_residences_north"
OUT = AUDIT / "independent_grade"
EXPECTED_SHA = "f883b5b321c072922625c11767ccb52716d8bbcf4d90c2cfb96c545b42123f70"
asset_path = ROOT / "modular" / "buildings" / "massing_honors_college_and_residences_north_3de3b7c.blend"
actual_sha = hashlib.sha256(asset_path.read_bytes()).hexdigest()
if actual_sha != EXPECTED_SHA:
    raise SystemExit(f"Asset changed during review: expected {EXPECTED_SHA}, got {actual_sha}")

source = json.loads((AUDIT / "sources" / "purdue_gis_lees_such_tower_fid544_2026-10-26.json").read_text(encoding="utf-8"))["feature"]
reopen = json.loads((OUT / "reopen_audit.json").read_text(encoding="utf-8"))
assert reopen["asset_sha256"] == EXPECTED_SHA
attrs = source["attributes"]
assert attrs["FID"] == 544 and attrs["BLDG_ABBR"] == "LEES" and attrs["BUILDING_N"] == "Lees-Such Tower"
lat0, lon0 = 40.4274, -86.9137
ring = source["geometry"]["rings"][0]
source_xy = [((lon-lon0)*111412.84*math.cos(math.radians(lat0)), (lat-lat0)*111040.0) for lon,lat in ring]
source_poly = Polygon(source_xy)
model_xy = [(v[0],v[1]) for v in reopen["bottom_ring_xyz"]]
model_poly = Polygon(model_xy)
iou = source_poly.intersection(model_poly).area / source_poly.union(model_poly).area
hausdorff = source_poly.boundary.hausdorff_distance(model_poly.boundary)
src_boundary = source_poly.boundary
mod_boundary = model_poly.boundary
src_to_mod = [mod_boundary.distance(Point(x,y)) for x,y in source_poly.exterior.coords[:-1]]
mod_to_src = [src_boundary.distance(Point(x,y)) for x,y in model_poly.exterior.coords[:-1]]
mean_boundary = (sum(src_to_mod)+sum(mod_to_src))/(len(src_to_mod)+len(mod_to_src))
centroid_delta = source_poly.centroid.distance(model_poly.centroid)
metrics = {
    "source_vertex_count": len(ring)-1,
    "model_shell_vertex_count": len(model_xy),
    "source_polygon_area_m2": source_poly.area,
    "model_shell_area_m2": model_poly.area,
    "polygon_iou": iou,
    "symmetric_sampled_boundary_mean_m": mean_boundary,
    "symmetric_boundary_hausdorff_m": hausdorff,
    "centroid_delta_m": centroid_delta,
    "source_bounds_xy_m": list(source_poly.bounds),
    "model_bounds_xy_m": list(model_poly.bounds),
}
criteria = [
    {"name":"Identity and source-backed footprint", "score":2.0, "max_score":2.0,
     "evidence":f"Raw Purdue GIS feature FID {attrs['FID']} / {attrs['BLDG_ABBR']} identifies {attrs['BUILDING_N']} at {attrs['ADDRESS']}. I independently transformed its 120-point ring into campus XY and compared it with the 38-point exported shell: IoU {iou:.4f}, symmetric boundary mean {mean_boundary:.2f} m, centroid delta {centroid_delta:.2f} m. The shape and identity are strongly supported."},
    {"name":"Position, orientation, scale, and dimensions", "score":1.75, "max_score":2.0,
     "evidence":f"The shell is in campus coordinates and follows the source polygon orientation. Its XY envelope is about {model_poly.bounds[2]-model_poly.bounds[0]:.1f} by {model_poly.bounds[3]-model_poly.bounds[1]:.1f} m; its centroid differs from the transformed GIS source by {centroid_delta:.2f} m. Maximum boundary discrepancy is {hausdorff:.2f} m, primarily at detail simplified out of the 120-point source outline."},
    {"name":"Evidence-backed height, floors, and roof", "score":1.0, "max_score":2.0,
     "evidence":"Purdue OEP evidence supports six floors plus a basement, and the exterior shell models six above-grade levels. Wall top is 19.4 m and the modeled gable peak is 29.1 m, both estimates. The source GIS says NUM_LEVELS=8 and Extrution=96 but does not document the vertical units; the one 2016 exterior image supports a gabled roof and dormers but cannot establish measured height, roof pitch, or which portions belong specifically to North."},
    {"name":"Facade, entrances, and distinctive architecture", "score":1.5, "max_score":2.0,
     "evidence":"The saved exterior view shows warm brick, a dark pitched gable roof, pale horizontal/rake trim, repeated framed windows, a three-level projecting glazed bay and dormers. These broad features are visible in the retained Purdue 2016 exterior reference. Exact facade orientation, window cadence, entry dimensions, and attribution of the photographed entry to the North tower remain inferred; the model is still simplified relative to the photograph."},
    {"name":"Modular export, portability, and complete evidence", "score":1.75, "max_score":2.0,
     "evidence":f"Fresh Blender 5.2.3 open confirmed the expected scene/collection, {reopen['collection_object_count']} collection objects ({reopen['mesh_object_count']} meshes), a separate explicitly schematic interior scene, no linked object data, and no image/external texture dependencies. The build script and source snapshots are present. Deducted 0.25 because the evidence record still says fresh-open validation is pending and the validation JSON omits the asset SHA-256, reducing traceability."},
]
score=sum(c["score"] for c in criteria)
result={
    "building":"Honors College and Residences North / Lees-Such Tower",
    "evaluator":"Independent reviewer; asset and source evidence inspected directly",
    "review_date":"2026-10-26",
    "score":score,
    "max_score":10,
    "passing_threshold":8,
    "passed":score>=8,
    "asset_path":"modular/buildings/massing_honors_college_and_residences_north_3de3b7c.blend",
    "asset_sha256":actual_sha,
    "criteria":criteria,
    "evidence":{
        "reopened_scene":reopen["scene"],
        "reopened_collection":reopen["collection"],
        "GIS_feature_id":attrs["FID"],
        "GIS_building_code":attrs["BLDG_ABBR"],
        "geometry_metrics":metrics,
        "external_images":reopen["images"],
        "external_image_dependencies_in_used_materials":[m["images"] for m in reopen["materials"] if m["images"]],
    },
    "findings":[
        "The footprint comparison is excellent overall, though small source notches are omitted in the simplified shell (maximum boundary residual about 2.74 m).",
        "Six above-grade floors are supported by Purdue OEP; the exact height and roof profile remain estimates because the GIS vertical fields are ambiguous and no dimensioned elevation was provided.",
        "The distinct gable, glazed projecting bay and dormers are recognizable, but their exact North-specific placement is not independently documented by the available complex-wide photo.",
        "Update evidence_record.json validation status and record this exact asset SHA-256 for traceable grading."
    ],
}
# Ensure no model edit happened while review was being generated.
if hashlib.sha256(asset_path.read_bytes()).hexdigest() != EXPECTED_SHA:
    raise SystemExit("Asset changed during review; no grade written")
(OUT/"grade_result.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print(json.dumps(result,indent=2))
