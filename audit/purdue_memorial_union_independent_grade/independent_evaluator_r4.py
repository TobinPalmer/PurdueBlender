from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CRITERIA = [
    {
        "name": "Identity and source-backed footprint",
        "score": 1.8,
        "max_score": 2.0,
        "evidence": "The model remains recognizable as the Purdue Memorial Union tower-and-wings complex. The supplied historic Purdue GIS phases and immutable baseline support the retained shell. Independent Blender reopen measured all 18 original wall/base bounds unchanged at 0.0 m delta; three documented bases are additive. The historical GIS match is approximate, not a current survey.",
    },
    {
        "name": "Placement, orientation, and scale",
        "score": 1.9,
        "max_score": 2.0,
        "evidence": "The saved asset root reopened at identity transform. The read-only master-marker record has one Placement_purdue_memorial_union at (205.75, -271.65, 0), zero rotation and unit scale, linked to the expected collection/library. This pass did not reopen the current master, so integration remains a coordinator check.",
    },
    {
        "name": "Evidence-backed height, floors, and roof form",
        "score": 1.2,
        "max_score": 2.0,
        "evidence": "R4 adds narrow flashing at roof intersections and retains separate low-pitch gables. The fresh south/west obliques still show very broad, largely uninterrupted blue roof planes and abrupt courtyard transitions; the roof silhouette does not yet read cleanly as the distinct wings shown in the dated references. Aggregate 29.5 m height, floor spacing, eaves, ridges and junction positions are explicitly estimates, not measured elevations.",
    },
    {
        "name": "Facade rhythm, entrance, and distinctive architecture",
        "score": 1.6,
        "max_score": 2.0,
        "evidence": "The south facade has arched window bays, glazed multi-tier tower openings, a framed entry, dormers supported by the 1924 photo, and new paired relief silhouettes informed by the 2024 Purdue image. Brick and slate have visible surface texture. The relief silhouettes remain far simpler than the photographed carved groups; tower mullion proportions, stone ornament, side-window rhythm and large west-wall areas remain schematic or unverified. The detailed front still reads as a simplified interpretation rather than a close facade reconstruction.",
    },
    {
        "name": "Modular portability and evidence/validation",
        "score": 1.5,
        "max_score": 2.0,
        "evidence": "Independent Blender 5.2.3 reopen confirms the exact requested SHA, 650 collection objects/608 meshes, identity root, no materialless meshes, no unpacked external images, and unchanged baseline wall/base bounds. R4 evidence records provenance and uncertainties. The shared manifest still reports the old 414-object unverified PMU asset without a hash or grade path, so the coordinator must refresh indexes and reopen the master before accepting integration.",
    },
]

def evaluate() -> dict:
    score = round(sum(c["score"] for c in CRITERIA), 1)
    return {
        "asset": "modular/buildings/purdue_memorial_union.blend",
        "sha256": "7e0e03969cad5846edacc38a4945f2c9021e48877c022cc79035d10e144eb480",
        "score": score,
        "max_score": 10.0,
        "pass_threshold": 8.0,
        "passed": score >= 8.0,
        "criteria": CRITERIA,
        "evidence": {
            "fresh_independent_reopen": "audit/purdue_memorial_union_independent_grade/independent_reopen_r4.json",
            "builder_validation": "audit/purdue_memorial_union_refine/validation_r4.json",
            "source_and_method": "audit/purdue_memorial_union_refine/build_evidence.md",
            "r4_views": [
                "audit/purdue_memorial_union_refine/grader_south_oblique_r4.png",
                "audit/purdue_memorial_union_refine/grader_west_oblique_r4.png",
                "audit/purdue_memorial_union_refine/grader_roof_r4.png",
                "audit/purdue_memorial_union_refine/grader_courtyard_r4.png",
                "audit/purdue_memorial_union_refine/south_facade_detail_r4.png",
            ],
            "source_images": [
                "audit/purdue_memorial_union_refine/archives_postconstruction_1924.jpg",
                "audit/purdue_memorial_union_refine/official_centenary_exterior_2024.jpg",
            ],
            "shared_manifest": "modular/manifest.json; PMU still reports object_count 414 and accuracy_status unverified",
            "read_only_master_marker": "audit/purdue_memorial_union_independent_grade/master_marker_readonly.json",
        },
        "findings": [
            "Independent score: 8.0/10, narrowly meeting the requested pass threshold. This score does not mean every facade, roof, floor, or height detail is verified.",
            "R4's additional roof flashing and tower relief silhouettes improve the prior model, but the broad roof planes and courtyard transitions remain the strongest visual discrepancy in current oblique/top views.",
            "The paired reliefs are currently simple silhouettes rather than detailed groups like the 2024 Purdue photo; tower glazing and surrounding limestone ornament also remain schematic.",
            "Before master acceptance, the coordinator must update the shared manifest/building index to the 650-object asset and this grade, reload the master, and verify the linked collection and placement marker. The existing read-only marker record alone does not prove the current master was reopened.",
        ],
        "limitations": [
            "Historic GIS features are phase-specific and were converted with the project's approximate local tangent-plane formula; they do not establish current survey precision.",
            "The 1924 archival and 2024 campus images differ in date and viewpoint; they support qualitative facade/massing comparison, not measured elevations or roof dimensions.",
            "The 29.5 m aggregate top, floor spacing, eaves, ridges and roof junctions remain estimates; no measured elevation or roof plan was found in the cited sources.",
            "This reviewer did not edit the asset, master blend, manifest or shared indexes.",
        ],
    }

if __name__ == "__main__":
    result = evaluate()
    (HERE / "independent_grade_r4.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Independent grade — Purdue Memorial Union R4",
        "",
        f"**Score: {result['score']:.1f}/10 — {'meets' if result['passed'] else 'below'} the 8.0 pass threshold.**",
        "",
        f"Reviewed asset SHA-256: `{result['sha256']}`. I independently reopened the saved asset in Blender 5.2.3; results are in `independent_reopen_r4.json`. I compared the fresh R4 views against the cited Purdue Archives 1924 photo and Purdue University 2024 exterior image, and checked the prior review and R4 source/validation record.",
        "",
        "| Criterion | Score | Finding |",
        "|---|---:|---|",
    ]
    for c in CRITERIA:
        lines.append(f"| {c['name']} | {c['score']:.1f}/{c['max_score']:.1f} | {c['evidence']} |")
    lines += ["", "## Findings", ""]
    lines += [f"{i}. {v}" for i, v in enumerate(result["findings"], 1)]
    lines += ["", "## Review limits", ""]
    lines += [f"- {v}" for v in result["limitations"]]
    lines += ["", "Machine-readable scorecard: `independent_grade_r4.json`. Scoring function: `independent_evaluator_r4.py`.", ""]
    (HERE / "independent_grade_r4.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"score": result["score"], "passed": result["passed"], "criteria": [(c["name"], c["score"]) for c in CRITERIA]}, indent=2))
