"""Independent Alpha Epsilon Pi revision-2 rubric evaluator."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROBE = json.loads((HERE / "fresh_open_probe.json").read_text(encoding="utf-8"))
EVIDENCE = json.loads((ROOT / "audit" / "alpha_epsilon_pi" / "evidence.json").read_text(encoding="utf-8"))
EXPECTED_HASH = "8074f7c27f1b0ba25e0699f056db21611249679335d2796a035db4b40673a961"

def evaluate(probe, evidence):
    assert probe["asset_sha256"] == EXPECTED_HASH, "Candidate changed after revision-2 freeze."
    assert probe["building_id"] == "alpha_epsilon_pi"
    assert evidence["building_id"] == "alpha_epsilon_pi"
    assert probe["foundation_vertex_count"] == 60
    assert probe["max_corresponding_vertex_error_m"] < 1e-4
    assert not probe["missing_material_meshes"]
    assert not probe["mesh_parent_errors"]
    assert not probe["unpacked_external_images"]

    identity = {
        "score": 1.35,
        "max_score": 2.0,
        "evidence": [
            "Purdue BoilerLink's current AEPi page lists 1051 David Ross Road; its searchable page content was available on review date 2026-10-26.",
            "Official Purdue GIS FID 754 also lists 1051 David Ross Road, and the project's saved satellite overlay aligns its polygon with a visible roof.",
            "The same GIS feature's BUILDING_N label is Chi Phi, so address/roof correspondence does not conclusively resolve current occupancy.",
            "GIS FID 821 is a separate Alpha Epsilon Pi candidate at 116 Fowler Avenue and is documented as not used for this model."
        ],
        "findings": [
            "The current official address and GIS/address match support the selected footprint, but the official GIS name conflict and absence of recent direct occupancy evidence remain unresolved."
        ]
    }
    position = {
        "score": 2.0,
        "max_score": 2.0,
        "evidence": [
            f"Fresh-open geometry compares all {probe['foundation_vertex_count']} selected foundation ring vertices to GIS FID 754; maximum corresponding XY error is {probe['max_corresponding_vertex_error_m']:.3g} m.",
            f"The exported library declares local coordinates and placement origin {probe['placement_origin_xy_m']} m; fresh-open local bounds are {probe['bounds_local_m']} m.",
            "The local coordinate transform and foundation ring preserve the source plan outline and its orientation rather than scaling to an unrelated bounding box."
        ],
        "findings": [
            "The sub-millimetre comparison is to the GIS polygon transformed into the project frame; it does not establish the GIS roof/wall edge or survey accuracy."
        ]
    }
    roof = {
        "score": 1.4,
        "max_score": 2.0,
        "evidence": [
            "The attributed 2009 Purdue AEPi photograph supports a three-visible-story brick house with a mansard roof and dormer cues; it is historical style evidence only.",
            f"Fresh-open bounds reach {probe['bounds_local_m']['max'][2]:.2f} m; wall and roof components are separately modeled, with the chimney cap reaching {max(x['z_max'] for x in probe['vertical_components']):.2f} m.",
            "No surveyed elevation or current roof-height source was supplied; wall levels, roof breaks, dormers, chimney and total height remain estimates."
        ],
        "findings": [
            "Retain explicit estimated status for floor heights and roof geometry until a current elevation, measured plan, or suitably classified LiDAR surface is available."
        ]
    }
    brick = probe["brick_shader"]
    assert all(brick[k] for k in ("material_present", "uv_to_brick_vector", "brick_color_to_principled_base_color", "brick_factor_to_bump_height", "bump_to_principled_normal"))
    facade = {
        "score": 1.6,
        "max_score": 2.0,
        "evidence": [
            "The revised exterior preview now reads as horizontal red masonry at the saved camera distance; independent fresh-open node inspection confirms UV coordinates feed the Brick Texture, its color feeds Principled Base Color, and its factor drives bump relief.",
            f"Fresh-open object-name inspection found {probe['feature_counts']['windows']} facade window fronts, {probe['feature_counts']['window_acs']} AC units, {probe['feature_counts']['dormers']} dormer glazing objects and {probe['feature_counts']['entry_objects']} entrance-related objects.",
            "Fresh Blender renders from front, east, west and rear show fenestrated side/rear elevations and the mansard silhouette; exposed internal/recessed faces remain comparatively plain and are not supported by a current elevation.",
            "The visible entry, Greek-letter sign, projecting window treatments, dark shingle roof and masonry match the broad historic-photo cues, while exact bay/window rhythm and current materials remain unverified."
        ],
        "findings": [
            "The key revision-1 defect (brick appearing as vertical siding) is corrected. Side/rear details and exposed recessed surfaces remain schematic because current target-facing imagery and measured elevations are unavailable."
        ]
    }
    modular = {
        "score": 1.9,
        "max_score": 2.0,
        "evidence": [
            f"An independent Blender 5.2.3 process reopened the exact candidate SHA256 {probe['asset_sha256']} and found the expected scene, stable asset collection and local-coordinate flag.",
            f"The collection contains {probe['objects']} objects ({probe['mesh_objects']} meshes) and {probe['material_count']} referenced materials; missing-material meshes, mesh-parent errors and unpacked external images are all zero.",
            f"The audit includes current-address/GIS records, the geometry transform, fresh-open probe, exterior/interior views and four independent review renders; the asset has {probe['feature_counts']['interior_objects']} named representative interior objects.",
            "The interior is still illustrative rather than tied to a public floor plan, and this standalone grade does not establish integration into the campus master."
        ],
        "findings": [
            "The model is portable and its evidence is organized; confirm and document master integration separately. Interior room positions remain representative estimates."
        ]
    }
    criteria = {
        "identity_and_source_backed_footprint": identity,
        "position_orientation_and_plan_dimensions": position,
        "evidence_backed_height_floors_and_roof": roof,
        "facade_entrances_and_distinctive_architecture": facade,
        "modular_export_portability_and_complete_evidence": modular,
    }
    score = round(sum(c["score"] for c in criteria.values()), 2)
    findings = [f for c in criteria.values() for f in c["findings"]]
    return {
        "building_id": "alpha_epsilon_pi",
        "candidate_sha256": probe["asset_sha256"],
        "candidate_matches_frozen_revision_2": probe["asset_sha256"] == EXPECTED_HASH,
        "reviewer": "independent subagent; fresh-open inspection, source comparison, node-link inspection, and four review renders",
        "rubric": "AGENT.md, five criteria at 2 points each",
        "score": score,
        "max_score": 10.0,
        "threshold": 8.0,
        "status": "PASS" if score >= 8.0 else "NEEDS_REFINEMENT",
        "pass": score >= 8.0,
        "criteria": criteria,
        "evidence": [
            "audit/alpha_epsilon_pi/independent_grade_revision_2/fresh_open_probe.json",
            "audit/alpha_epsilon_pi/independent_grade_revision_2/front_review.png",
            "audit/alpha_epsilon_pi/independent_grade_revision_2/east_review.png",
            "audit/alpha_epsilon_pi/independent_grade_revision_2/west_review.png",
            "audit/alpha_epsilon_pi/independent_grade_revision_2/rear_review.png",
            "audit/alpha_epsilon_pi/evidence.json and evidence.md",
            "audit/alpha_epsilon_pi/purdue_gis_features_fid754_821.json and satellite_footprint_overlay.png",
            "Purdue BoilerLink AEPi listing: https://boilerlink.purdue.edu/organization/aepi",
            "Historical facade source: https://commons.wikimedia.org/wiki/File:PurdueAEPIhouse.jpg"
        ],
        "findings": findings,
        "limitations": [
            "FID 754's official GIS name is Chi Phi despite the matching current AEPi listing address; current occupancy remains unresolved.",
            "The 2009 photo supports historic design character but not current condition; height, roof breaks, exact facade details, and interior plan remain estimated.",
            "Campus master integration has not been assessed by this standalone-asset grade."
        ]
    }

RESULT = evaluate(PROBE, EVIDENCE)
(HERE / "result.json").write_text(json.dumps(RESULT, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
report = [
    "# Independent Alpha Epsilon Pi review — revision 2",
    "",
    f"**Score: {RESULT['score']:.2f}/10 — {'PASS' if RESULT['pass'] else 'NEEDS REFINEMENT'}.** Threshold: 8/10.",
    "",
    "The revision resolves the prior brick shader defect: the wall now reads as horizontal masonry, and the fresh-open node graph confirms the UV-to-brick and bump connections. The current official chapter listing and matching GIS address support the footprint, while GIS's conflicting Chi Phi label remains unresolved.",
    "",
    "| Criterion | Score | Assessment |",
    "| --- | ---: | --- |",
]
for key, criterion in RESULT["criteria"].items():
    report.append(f"| {key.replace('_', ' ')} | {criterion['score']:.2f}/2 | {criterion['evidence'][0]} |")
report += ["", "## Remaining uncertainties", ""]
for item in RESULT["limitations"]:
    report.append(f"- {item}")
report += ["", "## Required evaluator shape", "", "`evaluate(probe, evidence)` returns `{score, max_score, criteria, evidence, findings}` and validates the frozen candidate hash plus fresh-open checks."]
(HERE / "result.md").write_text("\n".join(report) + "\n", encoding="utf-8")
print(json.dumps({"score": RESULT["score"], "status": RESULT["status"], "criteria": {k: v["score"] for k, v in RESULT["criteria"].items()}}, indent=2))
