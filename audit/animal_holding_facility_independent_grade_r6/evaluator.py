"""Independent AHF R6 evaluation from a Blender reopen and raw source probes."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = Path(__file__).resolve().parent
BUILDING = ROOT / "audit/animal_holding_facility"


def evaluate():
    blender = json.loads((AUDIT / "blender_probe.json").read_text(encoding="utf-8"))
    source = json.loads((AUDIT / "source_probe.json").read_text(encoding="utf-8"))
    built = json.loads((BUILDING / "build_evidence.json").read_text(encoding="utf-8"))
    prior_search = json.loads((BUILDING / "sources/ahf_facade_source_search_2026-10-25.json").read_text(encoding="utf-8"))
    added_search = json.loads((BUILDING / "sources/ahf_additional_source_search_2026-10-26.json").read_text(encoding="utf-8"))

    assert blender["candidate_commit"] == "c40be18b4f6c70ae8a101d84549b3c89f25c0db5"
    assert blender["result"] == "PASS" and blender["fresh_scene_link"]["pass"]
    assert blender["boundary_edges"] == 0 and blender["nonmanifold_edges"] == 0
    assert source["source_outline_vertex_count"] == 16
    assert source["ndhm"]["samples"]["north_main"]["n"] == 614
    assert source["ndhm"]["samples"]["south_addition"]["n"] == 359
    assert added_search["retrieved"] == "2026-10-26"

    south_slopes = [source["ndhm"]["samples"]["south_addition"]["fits_by_bin_m"][k]["slope_percent_xy"][1]
                    for k in ("2.5", "5.0", "7.5", "10.0")]
    criteria = [
        {"name": "Correct identity and source-backed footprint", "points": 2.0, "max_points": 2,
         "assessment": f"Purdue GIS FID 266 and Purdue facilities history identify the Animal Holding Facility; Indiana's separate 2018 footprint independently corroborates it. The raw GIS outline has {source['source_outline_vertex_count']} vertices, and each transformed vertex is within {blender['source_ring_vertex_nearest_mesh_vertex_m']['max']:.6f} m of a reopened mesh vertex."},
        {"name": "Position, orientation, and scale/dimensions", "points": 2.0, "max_points": 2,
         "assessment": f"Reopened world bounds are X {blender['bounds_world_m'][0]}, Y {blender['bounds_world_m'][1]}, Z {blender['bounds_world_m'][2]} m. GIS source outlines preserve the modeled plan orientation; Purdue and Indiana footprints agree within 0.50 m centroid offset and 1.74 m maximum symmetric boundary residual. The model's roughly 0.18 m envelope expansion is documented as wall/trim thickness."},
        {"name": "Evidence-backed height, floors, and roof form", "points": 1.75, "max_points": 2,
         "assessment": f"Independent sampling of the raw 2018 Indiana 5-ft NDHM reproduces 614 north/main cells (median {source['ndhm']['samples']['north_main']['median_m']:.3f} m) and 359 south-addition cells (median {source['ndhm']['samples']['south_addition']['median_m']:.3f} m). Four spatial-bin sizes give south-zone Y trends of {min(south_slopes):.3f}% to {max(south_slopes):.3f}%; the saved asset models a low slope there. Purdue GIS reports one level. NDHM is a normalized surface raster rather than an eave survey, so exact structural pitch, zone seam, and roof heights remain estimates."},
        {"name": "Facade, entrances, and distinctive architecture", "points": 0.0, "max_points": 2,
         "assessment": "The saved asset is a neutral, unfenestrated envelope without a modeled entrance. The 2026-10-26 follow-up found a webcam view described as the Large Animal Hospital complex and State Budget Committee minutes describing a Phase III addition/renovation; neither identifies an AHF facade or supplies a plan/elevation. The earlier public search also documents a null archive image field. No facade features can be credited from this evidence."},
        {"name": "Modular export, portability, and complete evidence", "points": 2.0, "max_points": 2,
         "assessment": f"Blender {blender['blender_version']} reopened the expected named collection with {blender['object_count']} mesh object, {blender['vertices']} vertices, {blender['faces']} faces, no modifiers or external images, and zero boundary/non-manifold edges. The collection also links into a clean factory-startup scene. Building-specific evidence includes raw GIS, orthophoto, and NDHM snapshots, reproducible scripts, profile analyses, reopen checks, and a preview."},
    ]
    score = round(sum(c["points"] for c in criteria), 2)
    return {
        "building_id": "massing_animal_holding_facility_4733f46",
        "candidate_commit": "c40be18b4f6c70ae8a101d84549b3c89f25c0db5",
        "asset_blob_matches_candidate": True,
        "score": score,
        "max_score": 10,
        "passing_threshold": 8,
        "pass": score >= 8,
        "criteria": criteria,
        "evidence": {
            "blender_probe": "audit/animal_holding_facility_independent_grade_r6/blender_probe.json",
            "source_probe": "audit/animal_holding_facility_independent_grade_r6/source_probe.json",
            "render": "audit/animal_holding_facility_independent_grade_r6/reviewed_asset_preview.png (directly inspected; neutral blank envelope and two roof zones)",
            "orthophoto": "audit/animal_holding_facility_independent_grade_r6/reviewed_orthophoto_overlay.png (directly inspected; supports roof plan/color zones only)",
            "roof_zones": "audit/animal_holding_facility_independent_grade_r6/reviewed_roof_zones.png (directly inspected)",
            "build_evidence": "audit/animal_holding_facility/build_evidence.json",
            "facade_search_2026_10_25": "audit/animal_holding_facility/sources/ahf_facade_source_search_2026-10-25.json",
            "additional_search_2026_10_26": "audit/animal_holding_facility/sources/ahf_additional_source_search_2026-10-26.json",
            "additional_search_interpretation": "Adds project history/context but no identifiable facade, plan, elevation, or entrance evidence.",
        },
        "findings": [
            {"severity": "blocking-for-8/10", "finding": "No AHF-specific facade photograph, measured elevation, plan, or entrance evidence was found in the documented public searches. The building remains a blank envelope, so the facade criterion is unverified and the grade is below the 8/10 pass threshold."},
            {"severity": "minor", "finding": "The modeled south roof slope agrees with broad NDHM surface trends at four bin sizes, but the raster is not a structural roof or eave survey and may include equipment, normalization artifacts, or edge contamination."},
            {"severity": "minor", "finding": "The north/main roof is held at its median because its fitted trend is weak and unstable. The 2023 orthophoto supports roof color zones, not roof heights, structure, or exact seam."},
            {"severity": "positive-evidence", "finding": "The exact saved asset blob matches candidate c40be18; Blender reopened it with a closed manifold mesh and successfully linked the expected collection into a clean scene."},
        ],
    }


if __name__ == "__main__":
    result = evaluate()
    (AUDIT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
