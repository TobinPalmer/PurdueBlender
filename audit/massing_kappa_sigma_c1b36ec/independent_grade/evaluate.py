"""Independent rubric evaluation of the Kappa Sigma Blender library."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent


def evaluate(evidence, comparison, probe):
    """Return criterion scores, evidence, and findings for this asset."""
    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                "Purdue GIS FID 804 explicitly names Kappa Sigma (SOKS), 308 North St.",
                "The mesh bottom outline was independently checked against the saved GIS ring; the independent LiDAR footprint agrees at IoU 0.8294 and centroid separation 1.10 m.",
                "The rendered building sits at the same roof-envelope location in current orthophoto; source ring geometry is a suitable footprint proxy, though not a wall survey."
            ],
            "findings": ["The GIS and LiDAR outlines are roof-envelope proxies, not surveyed structural-wall lines."],
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                "Independent Blender reopen confirms identity object transform and campus-coordinate placement.",
                "The source-derived XY envelope is 42.53 x 22.70 m; independently reopened mesh bounds are 42.53 x 22.70 m.",
                "The Purdue ring is used without manual rotation or translation, and the aerial overlay supports the registration."
            ],
            "findings": ["XY dimensions inherit the limitations of the GIS roof envelope and approximate project coordinate conversion."],
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 1.0,
            "max_score": 2,
            "evidence": [
                "The archived chapter-house images visibly support three facade levels, multiple front gables, and a chimney.",
                "The massing represents those elements; the image evidence is qualitative and not a scaled elevation."
            ],
            "findings": ["Wall height (9.6 m), ridge height (12.0 m), and chimney height (13.7 m) are estimates; no elevation drawing or vertical survey was found. The height criterion is therefore only partially supported."],
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1.5,
            "max_score": 2,
            "evidence": [
                "Archived chapter-house photos support red brick, repeated light-trimmed windows, a central entrance, raised KΣ lettering, gables, and chimney.",
                "The preview includes these recognizable elements and a distinct entry."
            ],
            "findings": ["Window placement and facade rhythm are approximated. The photographed entry has an arched surround, while the model uses a simplified canopy/step; dimensions and present-day continuity are unknown."],
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                "Independent Blender 4.5.15 reopen found the expected scene, collection, and single Kappa Sigma mesh in the collection.",
                "The object is identity-transformed, has no modifiers, and the library has no external image dependencies.",
                "The evaluated mesh has 2,554 vertices, 1,855 faces, and reopened world bounds of X 353.57..396.11 m, Y -153.82..-131.12 m, Z 0..13.70 m.",
                "The building audit includes raw GIS/LiDAR/imagery snapshots, source metadata, footprint comparison, build/reopen records, and a rendered preview."
            ],
            "findings": ["No portability or export-contract defect found in the independent reopen."],
        },
    ]
    score = sum(item["score"] for item in criteria)
    return {
        "asset_id": "massing_kappa_sigma_c1b36ec",
        "evaluator": "independent subagent review",
        "rubric": "AGENT.md, five criteria scored out of 2",
        "score": score,
        "max_score": 10,
        "pass_threshold": 8,
        "status": "pass" if score >= 8 else "fail",
        "criteria": criteria,
        "evidence": {
            "model_path": "modular/buildings/massing_kappa_sigma_c1b36ec.blend",
            "builder_path": "modular/buildings/build_massing_kappa_sigma_c1b36ec.py",
            "audit_path": "audit/massing_kappa_sigma_c1b36ec",
            "preview_reviewed": "audit/massing_kappa_sigma_c1b36ec/kappa_sigma_preview.png",
            "orthophoto_overlay_reviewed": "audit/massing_kappa_sigma_c1b36ec/sources/orthophoto_with_purdue_outline.png",
            "facade_photos_reviewed": [
                "audit/massing_kappa_sigma_c1b36ec/sources/kappa_sigma_chi_chapter_house_official.jpg",
                "audit/massing_kappa_sigma_c1b36ec/sources/kappa_sigma_chi_chapter_house_event_official.jpg"
            ],
            "independent_blender_probe": "audit/massing_kappa_sigma_c1b36ec/independent_grade/blender_probe.json",
            "gis_footprint_comparison": comparison["comparison"],
            "asset_contract_and_measurements": probe,
            "source_manifest_entries": len(evidence["sources"]),
        },
        "findings": [
            "The asset passes the 8/10 threshold at 8.5/10.",
            "Unresolved vertical dimensions and detailed entrance/window geometry are explicitly uncertain and estimated.",
            "The chapter photo is undated, and the saved current-use sources conflict; the model preserves the stable GIS identity without asserting current fraternity use."
        ],
    }


def main():
    evidence = json.loads((AUDIT / "evidence.json").read_text(encoding="utf-8"))
    comparison = json.loads((AUDIT / "footprint_comparison.json").read_text(encoding="utf-8"))
    probe = json.loads((HERE / "blender_probe.json").read_text(encoding="utf-8"))
    result = evaluate(evidence, comparison, probe)
    (HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
