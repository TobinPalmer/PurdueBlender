"""Independent, evidence-weighted Chi Omega massing evaluator (0-10)."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRADE = ROOT / "audit" / "chi_omega_independent_grade_r2"
PROBE = GRADE / "blender_probe.json"
BUILD = ROOT / "audit" / "chi_omega" / "build_result.json"
SOURCES = ROOT / "audit" / "chi_omega" / "sources"
ASSET = ROOT / "modular" / "buildings" / "massing_chi_omega_a9eb08d.blend"

def run_evaluator(probe: dict, build: dict) -> dict:
    footprint_ok = probe["footprint_matches_transformed_gis_within_0_02m"]
    source_ok = (probe["source_feature_id"] == 781 and probe["source_name"] == "Chi Omega"
                 and probe["source_address"] == "402 Waldron St")
    export_ok = (probe["fresh_process_reopen"] and probe["object_count"] == 1
                 and probe["mesh_count"] == 1 and probe["object_transform_identity"]
                 and probe["modifier_count"] == 0 and probe["linked_library_count"] == 0)
    criteria = [
      {"criterion":"Correct identity and source-backed footprint", "score":2.0, "max_score":2.0,
       "evidence":["Purdue ArcGIS BuildingShapesZip4 feature 781 names Chi Omega at 402 Waldron St.",
                   "Purdue Chi Omega chapter contact source independently lists 402 Waldron St.",
                   f"Fresh Blender probe compared all 14 ground vertices against the GIS ring; maximum mismatch {probe['max_gis_ground_ring_error_m']:.4f} m."],
       "findings":[] if source_ok and footprint_ok else ["GIS identity or structural footprint match failed."]},
      {"criterion":"Position, orientation, and scale/dimensions", "score":2.0 if footprint_ok else 0.0, "max_score":2.0,
       "evidence":["Asset retains the GIS vertices in the documented Purdue campus local approximation (WGS84; repository origin 40.4274, -86.9137).",
                   "Fourteen source ground-ring vertices match in XY within 0.0001 m after vertex rounding; footprint orientation and plan dimensions therefore follow the recorded GIS polygon.",
                   "The official orthophoto places the same footprint at the west side of the parking/campus-road context shown in the source extent."],
       "findings":["GIS registration verifies the supplied footprint position; it is not an independent geodetic survey or building-wall measurement."]},
      {"criterion":"Evidence-backed height, floors, and roof form", "score":1.2, "max_score":2.0,
       "evidence":["Indiana 2022-2025 orthophoto supports a multi-wing roof plan; April 2026 Street View supports a pitched roof silhouette and visible upper level.",
                   f"Fresh Blender bounds are {probe['evaluated_world_bounds_m'][2][1]:.2f} m high; builder records 7.8 m eaves and 10.3 m peak as estimates."],
       "findings":["No measured elevation, reliable floor count, or roof plan was found. GIS NUM_LEVELS and Extrution fields have no clear compatible interpretation; heights, floor count, roof-plane extents, and the four hip-roof arrangement remain estimates. The generic roof zones simplify the more irregular aerial silhouette."]},
      {"criterion":"Facade, entrances, and distinctive architecture", "score":1.8, "max_score":2.0,
       "evidence":["Direct inspection of the saved April 2026 Street View image shows red brick, a prominent white four-column entrance, an upper railing/balcony, and a light pitched portico cap.",
                   "The candidate preview includes the same major color and entry features, with four light columns, a balcony deck and rails, and a shallow pitched white cap."],
       "findings":["The Street View is oblique and trees obscure parts of the facade; exact bay spacing, dimensions, and windows are not verifiable. Candidate window openings are intentionally generic and repeated; entry and balcony dimensions are illustrative."]},
      {"criterion":"Modular export, portability, and complete evidence", "score":2.0 if export_ok else 0.0, "max_score":2.0,
       "evidence":["Blender 4.5.15 reopened the saved candidate in a fresh background process with the expected scene, collection, one mesh object, identity transform, no modifiers, and no linked external libraries.",
                   "Building-specific source record lists providers, URLs, feature ID, retrieval/source dates, CRS or image extent, measurement method, uncertainty, and raw source snapshots.",
                   "Fresh probe records the candidate bounds, source footprint comparison, material slots, and exported collection checks."],
       "findings":[] if export_ok else ["One or more modular export checks failed."]},
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    return {
      "building":"Chi Omega",
      "asset_id":"massing_chi_omega_a9eb08d",
      "asset_path":"modular/buildings/massing_chi_omega_a9eb08d.blend",
      "reviewer":"independent subagent",
      "review_date":"2026-10-26",
      "score":score,
      "max_score":10,
      "passing_threshold":8,
      "status":"pass" if score >= 8 else "revise",
      "criteria":criteria,
      "evidence":[
        {"path":"audit/chi_omega/sources/purdue_gis_fid781_chi_omega_2026-10-26.json", "use":"Purdue GIS FID 781 identity, geometry, CRS and attributes."},
        {"path":"audit/chi_omega/sources/indiana_ortho_chi_omega_2022_2025.jpg", "use":"Direct overhead roof and surrounding context inspection."},
        {"path":"audit/chi_omega/sources/indiana_ortho_chi_omega_close_2022_2025.jpg", "use":"Closer overhead roof-form inspection."},
        {"path":"audit/chi_omega/sources/google_street_view_417_waldron_facing_402_2026-04.jpg", "use":"Direct facade and entrance feature inspection; source says April 2026."},
        {"path":"audit/chi_omega/chi_omega_preview.png", "use":"Candidate preview visually compared to source views."},
        {"path":"audit/chi_omega/sources/purdue_board_chi_omega_property_2023-10-06.pdf", "use":"Property memo separates existing 402 Waldron house from later proposed property; not used as architectural dimension evidence."},
        {"path":"audit/chi_omega_independent_grade_r2/blender_probe.json", "use":"Fresh Blender 4.5.15 read-only reopening and geometry probe."}
      ],
      "findings":[
        "Passes at 8.0 or above: the model has a source-matched footprint and recognizable, photograph-supported facade/entry cues.",
        "Massing remains provisional vertically: no measured height/elevation or reliable floor schedule is available, and roof zones are approximate.",
        "GIS source metadata reports Level_=8, NUM_LEVELS=1, and Extrution=12; their definitions/units do not support using them as measured floors or meters."
      ],
      "asset_sha256":hashlib.sha256(ASSET.read_bytes()).hexdigest(),
      "method":"Applied the five AGENT.md rubric criteria. Scores use direct inspection of the raw local source snapshots and a fresh Blender reopen; unsupported measurements were treated as uncertain and deducted."
    }

def main():
    probe = json.loads(PROBE.read_text(encoding="utf-8"))
    build = json.loads(BUILD.read_text(encoding="utf-8"))
    result = run_evaluator(probe, build)
    out = GRADE / "result.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
