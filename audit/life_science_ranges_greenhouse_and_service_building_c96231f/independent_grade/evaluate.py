from __future__ import annotations
import hashlib, json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit/life_science_ranges_greenhouse_and_service_building_c96231f"
ASSET = ROOT / "modular/buildings/massing_life_science_ranges_greenhouse_and_service_building_c96231f.blend"
EXPECTED_SHA256 = "5A33EFE401C37523D184430A692AD10FEA04A3F71F098E083B488D5064C38B1C"

def evaluate():
    sha = hashlib.sha256(ASSET.read_bytes()).hexdigest().upper()
    gis = json.loads((AUDIT / "sources/purdue_gis_fid915.geojson").read_text(encoding="utf-8"))
    feat = gis["features"][0]
    p = feat["properties"]
    assert feat["id"] == 915 and p["FID"] == 915 and p["BLDG_ABBR"] == "LSR"
    rings = feat["geometry"]["coordinates"]
    coords = [pt for ring in rings for pt in ring]
    lons, lats = [pt[0] for pt in coords], [pt[1] for pt in coords]
    coslat = math.cos(math.radians(40.4274))
    gis_width_m = (max(lons)-min(lons))*111412.84*coslat
    gis_height_m = (max(lats)-min(lats))*111040.0
    validation = json.loads((AUDIT / "fresh_open_validation.json").read_text(encoding="utf-8"))
    bounds = validation["bounds_m"]
    asset_width_m = bounds["X"][1]-bounds["X"][0]
    asset_height_m = bounds["Y"][1]-bounds["Y"][0]
    width_delta = asset_width_m-gis_width_m
    height_delta = asset_height_m-gis_height_m
    evidence_files = [
        "sources/purdue_gis_fid915.geojson", "sources/purdue_building_shapes_layer_metadata.json",
        "sources/esri_world_imagery_2026_extent.jpg", "sources/purdue_2022_board_project_approval.pdf",
        "sources/purdue_2026_greenhouse_social_photo.jpg", "sources/purdue_2026_greenhouse_conveyor.jpg",
        "previews/gis_footprint_overlay.jpg", "previews/board_exhibit-3.png",
        "previews/exterior_oblique.png", "previews/roof_plan.png", "previews/interior_research_bench.png",
        "fresh_open_validation.json"
    ]
    evidence_present = {f: (AUDIT/f).exists() for f in evidence_files}
    criteria = [
      {"name":"Correct identity and source-backed footprint", "points":2.0, "max_points":2,
       "evidence":"Official Purdue GIS feature 915 identifies BLDG_ABBR LSR, BUILDING_N Life Science Ranges, address 180 S Russell Street. The saved aerial and GIS overlay locate the feature on the greenhouse complex; board Exhibit A names the facility and ranges.",
       "findings":"Identity and footprint are strongly supported. GIS feature has an outer ring and an internal ring; builder traces the envelope curb and draws range rows from the aerial."},
      {"name":"Position, orientation, and scale/dimensions", "points":1.5, "max_points":2,
       "evidence":f"Builder projects lon/lat into the project's local XY convention and derives origin from FID 915 bounds. Projected GIS envelope is {gis_width_m:.2f} m E-W by {gis_height_m:.2f} m N-S; model bounds are {asset_width_m:.2f} by {asset_height_m:.2f} m (delta {width_delta:+.2f}, {height_delta:+.2f} m). Rows are drawn in the same east-west orientation as the orthophoto.",
       "findings":"Asset-local dimensions and axes closely match GIS, but the candidate evidence does not verify the corresponding master placement marker or a direct top-down overlay of the new candidate geometry against GIS. The yellow outline in the saved overlay is explicitly the old massing bounds."},
      {"name":"Evidence-backed height, floors, and roof form", "points":1.0, "max_points":2,
       "evidence":"Purdue GIS records NUM_LEVELS=2 and Extrution=12 (the field's units/meaning are not documented in the saved evidence). The aerial, board plan, and Purdue photos support low multi-span pitched greenhouse roofs and a service wing.",
       "findings":"Builder uses 3.65 m eaves, 5.95 m greenhouse ridge, and 6.8 m service-wing height without a dimensioned section/elevation or verified interpretation of the GIS Extrution field. These are estimates; roof appearance is plausible but measured height and exact roof geometry remain unsupported."},
      {"name":"Facade, entrances, and distinctive architecture", "points":1.5, "max_points":2,
       "evidence":"2026 Purdue exterior photo shows glazed greenhouse framing, low opaque base, attached brick/service portion and facility sign. Conveyor photo supports the phenotyping equipment concept. Renders show glazing, repeated frames, service doors, louvers, sign and planted benches.",
       "findings":"Distinctive materials and greenhouse structure are recognizable. Some service-wing facade/entrance proportions and equipment placement are reconstructed from limited views rather than dimensioned or surveyed evidence; interior benches/plants are a plausible interpretation."},
      {"name":"Modular export, portability, and complete evidence", "points":1.5, "max_points":2,
       "evidence":f"Expected SHA-256 match: {sha == EXPECTED_SHA256}. Fresh-open report passes with {validation['objects']} objects, {validation['materials']} materials and {len(validation['external_unpacked_images'])} unpacked external image dependencies; expected scene/collection names are present. Required preview/source files: {sum(evidence_present.values())}/{len(evidence_present)} present.",
       "findings":"Modular collection and clean reopen are verified. Evidence is substantial, but the saved source notes do not consistently record exact source URLs/provider retrieval dates/source dates/CRS/method/uncertainty per AGENT.md. The existing overlay is not a candidate-asset-vs-GIS validation."}
    ]
    score = round(sum(c["points"] for c in criteria), 2)
    findings = [f for c in criteria for f in [c["findings"]] if f]
    result = {"score":score,"max_score":10,"passing_threshold":8,"status":"PASS" if score >= 8 else "REVISION_REQUIRED",
      "asset_path":str(ASSET),"asset_sha256":sha,"expected_sha256":EXPECTED_SHA256,
      "source_identity":{"feature_id":feat["id"],"building_abbr":p["BLDG_ABBR"],"building_name":p["BUILDING_N"],"address":p["ADDRESS"]},
      "measurements":{"gis_envelope_width_m":round(gis_width_m,3),"gis_envelope_height_m":round(gis_height_m,3),"asset_bounds_x_m":bounds["X"],"asset_bounds_y_m":bounds["Y"],"asset_width_m":round(asset_width_m,3),"asset_height_m":round(asset_height_m,3),"width_delta_m":round(width_delta,3),"height_delta_m":round(height_delta,3)},
      "criteria":criteria,"evidence_files":evidence_present,"findings":findings,
      "revision_requests":[
        "Provide a fresh candidate-asset top-down footprint overlay against GIS FID 915 (not the legacy massing outline), and verify the proposed origin against the master Placement marker or document that the master owner must apply it.",
        "Add authoritative height/section evidence or retain explicit estimated labels and document why the proposed 3.65 m / 5.95 m / 6.8 m values are reasonable; clarify the GIS Extrution=12 field units/meaning if possible.",
        "Complete per-source provenance with exact URL/provider, retrieval date, source date, CRS, measurement method, and uncertainty; ensure the saved evidence agrees with the candidate geometry and source interpretation."
      ],
      "remaining_uncertainties":["No dimensioned as-built elevations/sections found in the inspected evidence.","Greenhouse interior bench, plant, bay and equipment arrangement is inferred from public imagery and plans.","Master placement instance was not part of this independent asset-grade validation."]}
    return result

if __name__ == "__main__":
    result=evaluate()
    out=Path(__file__).with_name("grade_result.json")
    out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps({"score":result["score"],"status":result["status"],"asset_sha256":result["asset_sha256"],"measurements":result["measurements"]},indent=2))
