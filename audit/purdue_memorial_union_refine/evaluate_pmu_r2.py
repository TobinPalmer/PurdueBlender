from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CRITERIA = [
    {
        "name": "Identity and source-backed footprint",
        "score": 1.8,
        "max_score": 2.0,
        "evidence": "The asset reads as Purdue Memorial Union's central tower and wings. Historic Purdue Libraries GIS plus the immutable original structural-bounds record support the principal shell; independent R2 comparison finds all 18 original wall/base objects retained with 0.0 m bound delta. Historic GIS is approximate and does not validate later additions or a current survey.",
    },
    {
        "name": "Placement, orientation, and scale",
        "score": 1.9,
        "max_score": 2.0,
        "evidence": "Freshly reopened asset has identity root transform (zero location/rotation, unit scale). The read-only master marker record reports the PMU instance at (205.75, -271.65, 0), zero rotation, unit scale, and expected asset link. Master placement was not freshly reopened in this isolated R2 inspection, so retain a small verification deduction.",
    },
    {
        "name": "Evidence-backed height, floors, and roof form",
        "score": 1.2,
        "max_score": 2.0,
        "evidence": "R2 replaces five original roof objects with 20 separate roof objects including five lower wing gables and narrow eave/ridge caps; the south wing depth is corrected and the tower reads as a distinct higher mass. However, the south/west/roof renders still show broad, visually dominant slate planes and awkward roof intersections/open-courtyard transitions. The 29.5 m overall height, floor spacing, eaves and ridges are estimates; the historic photo is not a dimensioned elevation.",
    },
    {
        "name": "Facade rhythm, entrance, and distinctive architecture",
        "score": 1.4,
        "max_score": 2.0,
        "evidence": "Arched south-wing windows, limestone archivolts, staged multi-tier tower glazing and an articulated glazed entry are clear improvements and reflect the 1924 and 2024 Purdue images. In the renders, the long wings remain generic/repetitive, the tower glazing and portal are still simplified relative to the references, and side relief fields lack supported detail. The photos give qualitative, not measured, dimensions.",
    },
    {
        "name": "Modular portability and evidence/validation",
        "score": 1.6,
        "max_score": 2.0,
        "evidence": "The saved PMU asset independently reopens at SHA-256 9e68eac0b432b108dd1298b0b078f5337e2402d8063e6393f1abdb61f9667aaa with collection Asset_purdue_memorial_union, 577 objects/541 meshes, identity root, no unmaterialled meshes and no unpacked external images. Validation compares against the immutable original structural-bounds file, with 18/18 original wall/base bounds unchanged and three documented additive bases; cited source/provenance and remaining uncertainty are recorded. The shared modular manifest still reports stale object_count 414, and no current master reload was part of this grade.",
    },
]

def evaluate() -> dict:
    score = round(sum(c["score"] for c in CRITERIA), 1)
    findings = [
        "Score is 7.9/10, below the project's 8/10 pass threshold; this is an improvement over the 7.7 R1 grade but does not pass.",
        "Refine the roof silhouette and intersections further: make lower wing ridges/eaves legible from oblique views, reduce canopy-like broad planes, and clean the courtyard/central junction while retaining the corrected south-wing depth.",
        "Use the reference south elevation to improve tower glazing proportions, wing opening rhythm, and entrance/portal stone articulation; keep new sculptural detail limited to what the sources show.",
        "Keep total height, floor spacing, eave and ridge elevations explicitly estimated unless a measured elevation source is found.",
        "The shared modular manifest's PMU object_count (414) does not match the fresh asset inventory (577); coordinator should reconcile the index and reload the master after accepting the asset.",
    ]
    return {
        "asset": "modular/buildings/purdue_memorial_union.blend",
        "sha256": "9e68eac0b432b108dd1298b0b078f5337e2402d8063e6393f1abdb61f9667aaa",
        "score": score,
        "max_score": 10.0,
        "pass_threshold": 8.0,
        "passed": score >= 8.0,
        "criteria": CRITERIA,
        "evidence": {
            "fresh_reopen": "audit/purdue_memorial_union_refine/independent_reopen_r2.json",
            "r2_validation": "audit/purdue_memorial_union_refine/validation_r2.json",
            "immutable_original_bounds": "audit/purdue_memorial_union_independent_grade/structural_bounds.json (baseline asset SHA-256 b1afa1dcffd08626c7508153b3c4d3a59cac86d605b6553d7f3477a01d972a25)",
            "rendered_views": [
                "audit/purdue_memorial_union_refine/grader_south_oblique_r2.png",
                "audit/purdue_memorial_union_refine/grader_west_oblique_r2.png",
                "audit/purdue_memorial_union_refine/grader_roof_r2.png",
                "audit/purdue_memorial_union_refine/south_facade_detail_r2.png",
            ],
            "dated_photo_sources": [
                "Purdue Libraries Archives, 1924: https://i0.wp.com/blogs.lib.purdue.edu/news/files/2017/03/PPBUC00823.jpg?fit=1111%2C639&ssl=1",
                "Purdue University Stories, 2024: https://stories.purdue.edu/app/uploads/2024/09/Hero-PMU-7R0A0670-1920x1080-Option2.jpg",
            ],
            "source_provenance": "audit/purdue_memorial_union_refine/build_evidence.md",
            "manifest_object_count": 414,
        },
        "findings": findings,
        "limitations": [
            "The reviewed Purdue GIS records are historical and approximate; they support footprint/phase context, not present elevations or detailed roof dimensions.",
            "The 1924 archival photograph and 2024 centenary photograph differ in date and perspective, so architecture comparisons are qualitative.",
            "Master placement was supported by the prior read-only marker record; the master was not opened or modified for this grade.",
        ],
    }

if __name__ == "__main__":
    result = evaluate()
    (HERE / "independent_grade_r2.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"score": result["score"], "passed": result["passed"], "criteria": [(c["name"], c["score"]) for c in result["criteria"]]}, indent=2))
