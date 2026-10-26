"""Independent, evidence-based Sigma Nu Beta Zeta grading evaluator."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "audit" / "sigma_nu"
OUT = Path(__file__).resolve().parent / "independent_grade_r1.json"


def evaluate() -> dict:
    """Grade the saved Sigma Nu asset against AGENT.md's five 2-point criteria."""
    register = json.loads((EVIDENCE / "sources" / "source_register.json").read_text(encoding="utf-8"))
    gis = json.loads((EVIDENCE / "sources" / "purdue_gis_fid_758.json").read_text(encoding="utf-8"))
    validation = json.loads((EVIDENCE / "build_validation.json").read_text(encoding="utf-8"))

    source = next(s for s in register["sources"] if s.get("feature_id") == 758)
    attrs = gis["attributes"]
    # Directly reopened in Blender 5.2.3 for this review after the builder's
    # revised front-bearing update:
    # scene Building_massing_house_301841330_f58ae87; expected export
    # collection present with 34 mesh objects, 34 total, no modifiers or images.
    reopened = {
        "blender_version": "5.2.3 LTS",
        "scene": "Building_massing_house_301841330_f58ae87",
        "export_collection": "Asset_massing_house_301841330_f58ae87",
        "export_object_count": 34,
        "all_export_objects_are_meshes": True,
        "body_bounds_m": [33.777, 29.817, 7.2],
        "no_external_images": True,
    }

    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2.0,
            "evidence": [
                f"Purdue GIS FID {attrs['FID']} names {attrs['BUILDING_N']} / {attrs['BLDG_ABBR']} at {attrs['ADDRESS']}.",
                "The newsletter page shows the 1301 entrance sign and identifies Beta Zeta's chapter house in its text.",
                f"The closed source ring has {validation['source_polygon_vertices']} vertices; the saved base ring maximum symmetric nearest-vertex error is {validation['base_ring_max_vertex_error_m']:.8f} m.",
            ],
            "uncertainty": [
                "GIS is a building/roof polygon, not a surveyed structural-wall line; exact wall-to-roof offset remains unknown."
            ],
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 1.8,
            "max_score": 2.0,
            "evidence": [
                "The model uses the repository's documented local approximate geographic conversion from EPSG:4326; the transform is recorded in the source register.",
                f"Saved footprint vertices agree with the converted GIS ring within {validation['base_ring_max_vertex_error_m']:.8f} m, preserving its orientation and plan scale.",
                "The revised facade targets the approximately 20.715 m north/northwest-facing edge adjacent to Tower Drive; OSM road context offers directional support.",
            ],
            "uncertainty": [
                "The GIS coordinates are converted with a project-local approximation rather than a surveyed/projected CRS; no independent survey or wall-footprint check is provided. OSM context does not establish the facade bearing, so the front selection remains inferred."
            ],
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 0.6,
            "max_score": 2.0,
            "evidence": [
                f"The saved shell is {validation['estimated_wall_height_m']:.2f} m high with roof top at {validation['estimated_roof_height_m']:.2f} m; both are explicitly labeled estimates.",
                "The newsletter's exterior photographs are low-resolution oblique/cropped images and do not establish story heights or a roof silhouette.",
                "GIS fields NUM_LEVELS=1 and Extrution=44 have undocumented semantics and are correctly not treated as measured height evidence.",
            ],
            "uncertainty": [
                "Actual floor count, wall height, roof type, pitch/profile, and overall height are unverified. The flat low-cap roof in the preview is an interpretation, not a source-backed roof form."
            ],
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1.4,
            "max_score": 2.0,
            "evidence": [
                "Fall 2019 newsletter page 3 visually supports red/brown brick, a centered recessed/portico entrance, and pale horizontal/entrance trim at a broad level.",
                "The revised reopened preview points the entry facade toward the north/northwest edge selected from the GIS shape and Tower Drive context; it contains a centered recessed opening with piers/canopy and horizontal bands.",
            ],
            "uncertainty": [
                "The newsletter provides only limited oblique views; window count, spacing, dimensions, symmetry, trim material, and unseen elevations are not verified. The model's repeated two-row window pattern and detailed geometry exceed the available evidence."
            ],
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 2.0,
            "max_score": 2.0,
            "evidence": [
                f"Fresh Blender reopen confirmed scene {reopened['scene']}, named export collection {reopened['export_collection']}, and {reopened['export_object_count']} mesh objects.",
                "The expected campus-coordinate massing asset is saved at the manifest asset path; dedicated source script, validation JSON, preview render, source register, raw GIS snapshot, and newsletter raster are present.",
                "The collection uses no external images or other file dependencies, and the validation record includes bounds, source-ring error, reopening status, and unresolved uncertainty.",
            ],
            "uncertainty": [],
        },
    ]
    score = round(sum(c["score"] for c in criteria), 1)
    evidence = {
        "asset": "modular/buildings/massing_house_301841330_f58ae87.blend",
        "builder_script": "modular/buildings/build_massing_house_301841330_f58ae87.py",
        "preview": "audit/sigma_nu/sigma_nu_preview.png",
        "validation": "audit/sigma_nu/build_validation.json",
        "source_register": "audit/sigma_nu/sources/source_register.json",
        "gis_snapshot": "audit/sigma_nu/sources/purdue_gis_fid_758.json",
        "newsletter_snapshot": "audit/sigma_nu/sources/beta_zeta_fall_2019_newsletter_page2_900.jpg",
        "osm_road_snapshot": "audit/sigma_nu/sources/osm_tower_drive_way_327252145.json",
        "fresh_reopen_inspection": reopened,
        "identity_source": {
            "provider": source["provider"],
            "feature_id": source["feature_id"],
            "record_name": source["record_name"],
            "address": source["address"],
            "source_crs": source["source_crs"],
            "retrieval_date": source["source_retrieval_date"],
        },
        "unresolved_from_validation": validation["unresolved"],
    }
    findings = [
        "Below the 8/10 pass threshold: height, floor count, and roof silhouette have no authoritative dimensional/elevation evidence; the facade-bearing choice is contextually supported but remains inferred.",
        "For one iteration, keep the low-confidence height explicitly estimated, but seek a reliable elevation/roof source or simplify the roof to a neutral, clearly provisional mass. Do not infer height from the ambiguous GIS Extrution/NUM_LEVELS fields.",
        "Reduce or qualify the repeated front window count/spacing and trim specifics unless they can be corroborated by a clearer building-specific elevation/photo; preserve the directly visible brick and centered entry.",
        "Keep the GIS ring as a roof/building footprint proxy and report wall-line registration as unverified.",
    ]
    return {
        "building_id": "massing_house_301841330_f58ae87",
        "grader": "independent_grader",
        "grade_round": 1,
        "score": score,
        "max_score": 10,
        "passing_threshold": 8,
        "passed": score >= 8,
        "criteria": criteria,
        "evidence": evidence,
        "findings": findings,
    }


if __name__ == "__main__":
    result = evaluate()
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
