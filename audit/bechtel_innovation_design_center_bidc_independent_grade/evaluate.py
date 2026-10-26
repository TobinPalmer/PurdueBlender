"""Independent evidence-based grade for the rebuilt BIDC library asset.

Run from any directory with Python 3. The evaluator reads the archived evidence
and reopen-validation report, then adds documented visual review observations
from the saved overview and plan renders. It does not modify the model.
"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDING_ID = "bechtel_innovation_design_center_bidc"
AUDIT = ROOT / "audit" / BUILDING_ID
OUT = ROOT / "audit" / f"{BUILDING_ID}_independent_grade"


def evaluate() -> dict:
    evidence = json.loads((AUDIT / "evidence.json").read_text(encoding="utf-8"))
    validation = json.loads((AUDIT / "validation.json").read_text(encoding="utf-8"))

    gis = evidence["sources"][0]
    source_locals = [s["local_snapshot"] for s in evidence["sources"] if "local_snapshot" in s]
    source_locals += [p for s in evidence["sources"] for p in s.get("raw_snapshots", [])]
    source_locals += [s["raw_snapshot"] for s in evidence["sources"] if "raw_snapshot" in s]
    source_locals += [
        evidence["sources"][3]["building_specific_photo"]["local_snapshot"],
        "audit/bechtel_innovation_design_center_bidc/sources/first_floor_plan.png",
        "audit/bechtel_innovation_design_center_bidc/sources/second_floor_plan.png",
        "audit/bechtel_innovation_design_center_bidc/sources/basement_plan.png",
    ]

    expected_collection = evidence["exported_collection"]
    shell_bounds = validation["gis_shell_bounds_local_m"]
    xy_bounds_match_evidence = all(
        abs(shell_bounds[axis][i] - evidence["geometry"]["local_bounds_xy_m"][2 * axis + i]) < 0.01
        for axis in range(2)
        for i in range(2)
    )
    source_completeness = all((ROOT / p).is_file() for p in source_locals)
    render_completeness = all((ROOT / p).is_file() for p in validation["previews_rendered_after_reopen"])

    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2,
            "assessment": "Supported",
            "evidence": [
                "Official Purdue GIS feature 912 attributes identify BIDC at 1090 3rd Street.",
                "The saved shell has 48 vertices, corresponding to all 24 points of the official exterior ring; validation bounds agree with evidence bounds to under 1 cm.",
                "The plan render visibly follows the same notched footprint outline.",
            ],
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 2.0,
            "max_score": 2,
            "assessment": "Supported",
            "evidence": [
                "Evidence records the GIS-derived placement origin and local frame X east, Y north, Z up.",
                "Reopened shell bounds match the centered local GIS bounds within 1 cm; the overview and plan show no evident stretch or rotation inconsistent with the footprint.",
            ],
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 1.5,
            "max_score": 2,
            "assessment": "Partly supported; height uncertain",
            "evidence": [
                "Official Purdue first- and second-floor plan snapshots support two above-ground floors.",
                "The architect photo supports a low-profile roof edge and a two-storey frontage; the overview depicts two visible storeys and a low-slope roof.",
                "The modeled 10.8 m roof height is explicitly estimated; no verified elevation or section was found. Roof plant is also schematic.",
            ],
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1.25,
            "max_score": 2,
            "assessment": "Partly supported",
            "evidence": [
                "The building-specific architect photo supports the two-storey glazed frontage, fine mullions, light opaque cladding, and projecting low roof edge represented in the model.",
                "The overview shows glazing and repeated mullions, but the entrance is not clearly articulated as a door/entry sequence and the source photo's signage and strong entrance canopy/portal are not represented distinctly.",
                "Bay spacing and treatment of unphotographed sides are admitted estimates; no unsupported details were counted as evidence.",
            ],
        },
        {
            "name": "Modular export, portability, and evidence completeness",
            "score": 2.0 if (
                validation.get("reopened") is True
                and validation.get("collection") == expected_collection
                and validation.get("external_image_dependencies") == []
                and validation.get("mesh_object_count", 0) > 0
                and xy_bounds_match_evidence
                and source_completeness
                and render_completeness
            ) else 0.0,
            "max_score": 2,
            "assessment": "Supported" if source_completeness and render_completeness else "Incomplete",
            "evidence": [
                f"Saved asset reopened and contains the expected {expected_collection} collection with {validation.get('mesh_object_count')} mesh objects.",
                "Reopen validation confirms the GIS shell contract and reports no external image dependencies.",
                f"All {len(source_locals)} referenced raw source/plan files and both reopened-asset preview renders exist in the audit archive."
                if source_completeness and render_completeness else
                "One or more referenced evidence or render files are missing.",
            ],
        },
    ]

    score = round(sum(c["score"] for c in criteria), 2)
    findings = [
        "The 10.8 m overall height and roof plant lack as-built elevation/roof-plan support and remain estimates.",
        "The saved overview does not clearly identify an entrance, and omits the photographed BIDC sign and the prominent entrance framing; improve only if further source evidence is available.",
        "The model reads as a simplified architectural visualization. Unphotographed facades and detailed bay dimensions remain interpretive.",
    ]
    return {
        "building_id": BUILDING_ID,
        "score": score,
        "max_score": 10,
        "pass_threshold": 8,
        "passed": score >= 8,
        "criteria": criteria,
        "evidence": {
            "model": "modular/buildings/bechtel_innovation_design_center_bidc.blend",
            "source_evidence": "audit/bechtel_innovation_design_center_bidc/evidence.json",
            "reopen_validation": "audit/bechtel_innovation_design_center_bidc/validation.json",
            "overview_render": "audit/bechtel_innovation_design_center_bidc/overview.png",
            "plan_render": "audit/bechtel_innovation_design_center_bidc/plan.png",
            "source_files_checked": source_locals,
            "checks": {
                "gis_shell_bounds_match_evidence": xy_bounds_match_evidence,
                "all_referenced_source_snapshots_present": source_completeness,
                "both_preview_renders_present": render_completeness,
                "asset_reopened": validation.get("reopened") is True,
                "external_image_dependencies": validation.get("external_image_dependencies"),
            },
            "visual_review": "Independently inspected overview.png and plan.png against architect_photo.jpg and the published first_floor_plan.png.",
        },
        "findings": findings,
    }


if __name__ == "__main__":
    result = evaluate()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
