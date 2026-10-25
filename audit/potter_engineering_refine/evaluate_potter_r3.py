"""Independent evidence-based rubric evaluator for Potter Engineering R3.

This intentionally combines automated checks from an independently reopened
Blender asset with a documented manual comparison of source imagery/plans.
It does not modify the Blender asset or shared project indexes.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit/potter_engineering_refine"
ASSET = ROOT / "modular/buildings/potter_engineering.blend"
EXPECTED_SHA256 = "DB9C22C8CD12012120E3A020DD0D901DB4248FEED1156F0235DDF4A2CE92DC3F"


def evaluate():
    probe = json.loads((AUDIT / "independent_grade_probe.json").read_text())
    manifest = json.loads((ROOT / "modular/manifest.json").read_text())
    official = json.loads((ROOT / "audit/official_building_references.json").read_text())
    asset_entry = next(a for a in manifest["assets"] if a["id"] == "potter_engineering")
    reference = next(b for b in official["buildings"] if b.get("code") == "POTR")

    expected_shell = [
        [reference["aabb_xy_m"][0] - asset_entry["placement_origin_xy_m"][0],
         reference["aabb_xy_m"][2] - asset_entry["placement_origin_xy_m"][0]],
        [reference["aabb_xy_m"][1] - asset_entry["placement_origin_xy_m"][1],
         reference["aabb_xy_m"][3] - asset_entry["placement_origin_xy_m"][1]],
    ]
    observed_shell = probe["shell_world_bounds_m"][:2]
    shell_match = all(
        abs(expected_shell[axis][end] - observed_shell[axis][end]) < 0.002
        for axis in range(2) for end in range(2)
    )
    probes_pass = (
        probe["asset_sha256"] == EXPECTED_SHA256
        and probe["collection_objects"] == asset_entry["object_count"] == 500
        and probe["root_location"] == [0.0, 0.0, 0.0]
        and not probe["materialless_meshes"]
        and not probe["missing_external_images"]
        and probe["roof_opening_test"]["opening_center_clear"]
        and probe["roof_opening_test"]["west_control_intersects_roof"]
        and probe["roof_opening_test"]["east_control_intersects_roof"]
    )

    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2.0,
            "evidence": [
                f"Official Purdue-linked GIS snapshot identifies A. A. Potter Engineering Center, code POTR, feature {reference['fid']}.",
                f"Independently reopened structural shell XY bounds match the GIS envelope after manifest placement offset within 2 mm: {shell_match}.",
                "Historic 2016 plan overlays record IoU 0.757 for basement and 0.854–0.855 for upper plans; plan alignment is approximate and those plans are not current measured records.",
            ],
            "limitations": ["GIS polygon is a campus-map reference, not a certified survey."],
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "score": 1.8,
            "max_score": 2.0,
            "evidence": [
                "The independent Blender reopen confirmed the asset root at local (0,0,0).",
                f"Manifest placement offset is {asset_entry['placement_origin_xy_m']} m; asset shell aligns with the official GIS XY envelope after applying it.",
                f"GIS minimum rotated rectangle orientation is {reference['minimum_rotated_rectangle']['angle_degrees_east_ccw']:.3f}° east-CCW, consistent with the modeled north-south long axis.",
            ],
            "limitations": ["The master collection-instance marker itself was not opened by this grader; coordinator must confirm final scene placement during integration."],
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "score": 1.3,
            "max_score": 2.0,
            "evidence": [
                "Purdue's 2016 renovation study provides floor plans, a typical window schedule, and a penthouse plan; the official photo supports the broad, low roof profile.",
                "The asset contains floor slabs through the upper levels and a penthouse/roof interface; independently reopened structural shell top is 13.411 m and roof bounds reach 13.661 m locally.",
            ],
            "limitations": ["GIS explicitly marks height unverified; modeled elevations are estimates. The broad roof and penthouse height have no current surveyed elevation/as-built verification."],
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 1.1,
            "max_score": 2.0,
            "evidence": [
                "The archived Purdue Engineering photo supports red brick, pale precast surrounds, repeated punched windows, and the projecting rounded brick stair tower; these feature families are present in the exterior render.",
                "Facade close-up shows repeated brick piers, pale panels, window openings and a coherent material palette.",
            ],
            "limitations": ["The reference photo's bearing is unknown. The recognizable main exterior stair and canopy are not modeled in a verified facade position; the resulting entry presentation remains incomplete."],
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 1.8,
            "max_score": 2.0,
            "evidence": [
                f"Independent Blender 5.2.3 read-only reopen confirmed {probe['collection_objects']} collection objects / {probe['collection_meshes']} meshes, correct export collection, unchanged root, and matching SHA-256.",
                "All mesh objects have materials; there are no missing external image dependencies.",
                "Building-specific evidence records source URLs/providers, GIS feature ID, snapshot date, coordinate conversion, plan-registration method/uncertainty, image, validation, and an updated S03 route schematic.",
                f"The estimated S03 roof opening passes a center ray while both controls hit the roof: {probe['roof_opening_test']}.",
            ],
            "limitations": ["The post-R8 schematic/check is current, but the saved exterior render was not regenerated with this exact final asset revision."],
        },
    ]
    score = round(sum(c["score"] for c in criteria), 1)
    findings = [
        "The widened S03 roof opening resolves the earlier sampled roof-edge intersection at the tested center point; controls verify that roof mesh remains on both sides.",
        "A separate saved geometry check shows the estimated 0.8 m proxy can turn on the modeled landing and pass through the estimated 1.2 m doorway. This is not a continuous all-flight collision audit or code/accessibility certification.",
        "The model is strong on GIS footprint and modular integrity, but the primary entrance canopy/stair location is still unverified and absent, and building heights/upper details remain estimates.",
    ]
    return {
        "building": "Potter Engineering Center",
        "asset": "modular/buildings/potter_engineering.blend",
        "asset_sha256": probe["asset_sha256"],
        "score": score,
        "max_score": 10,
        "pass_threshold": 8,
        "passed": score >= 8 and probes_pass and shell_match,
        "criteria": criteria,
        "evidence": {
            "independent_blender_probe": "audit/potter_engineering_refine/independent_grade_probe.json",
            "source_review": "audit/potter_engineering_refine/SOURCE_REVIEW.md",
            "official_potter_gis_feature": reference["fid"],
            "gis_shell_envelope_match_with_manifest_offset": shell_match,
            "validator_checks_pass": probes_pass,
            "visuals_reviewed": [
                "audit/complete_potter/after.png",
                "audit/batch4_potter/exterior_facade_round7_low.png",
                "audit/batch4_potter/facade_detail_current.png",
                "audit/batch4_potter/stairwell_circulation_round7.png",
                "audit/complete_potter/interior_historic2016.png",
                "audit/potter_engineering_refine/purdue_potter_exterior.jpg",
                "audit/potter_engineering_refine/first_floor_plan_crop.png",
                "audit/potter_engineering_refine/s03_upper_route_schematic.png",
            ],
        },
        "findings": findings,
        "limitations": [
            "No current measured elevation or as-built roof plan was found.",
            "Some interior geometry derives from 2016 plans; current partitions and complete fit-out are unverified/incomplete.",
            "The main entrance photo cannot be registered to a compass facade; entry stair/canopy location is unresolved.",
            "The S03 check is local to the saved roof aperture and estimated door route; other stair/wall intersections from prior audits remain unresolved or based on historical plan traces.",
        ],
    }


if __name__ == "__main__":
    result = evaluate()
    out = AUDIT / "independent_grade_r3.json"
    out.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
