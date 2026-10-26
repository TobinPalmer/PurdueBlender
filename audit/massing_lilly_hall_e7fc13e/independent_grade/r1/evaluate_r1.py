"""Independent Lilly Hall r1 rubric evaluator.

Uses the saved source snapshot and a fresh Blender reopen report. Scores evidence,
not visual plausibility alone. Run with the repository Python interpreter.
"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
AUDIT = ROOT / "audit" / "massing_lilly_hall_e7fc13e"
OUT = AUDIT / "independent_grade" / "r1" / "grade.json"


def evaluate() -> dict:
    evidence = json.loads((AUDIT / "evidence.json").read_text(encoding="utf-8"))
    reopen = json.loads((AUDIT / "reopen_validation.json").read_text(encoding="utf-8"))
    gis = json.loads((AUDIT / "sources" / "purdue_gis_fid_581.json").read_text(encoding="utf-8-sig"))
    feature = gis["features"][0]
    attrs = feature["attributes"]
    ring_count = len(feature["geometry"]["rings"][0]) - 1
    max_error = float(reopen["max_nearest_vertex_difference_m"])
    is_fid_match = attrs.get("FID") == 581 and attrs.get("BLDG_ABBR") == "LILY"
    is_open = reopen.get("status") == "PASS" and reopen.get("collection") == evidence["collection"]
    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 2.0 if is_fid_match and ring_count == 34 and max_error < 0.002 else 0.0,
            "max_score": 2,
            "evidence": [
                "Saved Purdue GIS BuildingShapesZip4 feature FID 581 identifies BLDG_ABBR LILY, Lilly Hall of Life Sciences, at 915 Mitch Daniels Blvd.",
                f"The model shell follows the saved 34-vertex exterior ring; independent reopen report gives maximum nearest-vertex error {max_error:.6f} m and reports a closed manifold.",
                "Purdue Biological Sciences contact page corroborates the name and address; saved archival Purdue Libraries photo is a separate identity/character reference.",
            ],
            "findings": [],
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 2.0 if max_error < 0.002 and is_open else 1.5,
            "max_score": 2,
            "evidence": [
                "GIS EPSG:3857 ring was independently transformed with the documented repository local campus conversion and matches the shell coordinates within the reported tolerance.",
                "The outline preserves the GIS orientation and full footprint extent; no survey or measured wall offset is available, so this validates the massing outline and campus frame rather than surveyed façade dimensions.",
            ],
            "findings": [
                "The shared manifest still lists different bounds (approximately X -451.379..-320.881, Y -518.324..-408.905, Z 0..16) than the reopened asset (X -458.888..-320.999, Y -518.187..-408.020, Z 0..25.055). Coordinator should reconcile shared manifest metadata before integration."
            ],
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 1.25,
            "max_score": 2,
            "evidence": [
                f"Purdue GIS reports CountOfFLO={attrs.get('CountOfFLO')} and six occupied floors; this supports the represented floor count.",
                "The saved GIS has R=82.2 and floor levels in 12-unit increments, but publishes no units. The 25.055 m height comes from interpreting R as feet; that remains an estimate, not a measured height.",
                "The exterior footprint/GIS polygon does not establish roof pitch, setbacks, or rooftop plant. The model uses a single flat top; roof articulation is unverified.",
            ],
            "findings": ["Height and roof form remain partly unverified because the source field units and roof geometry are undocumented."],
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1.25,
            "max_score": 2,
            "evidence": [
                "Archival Purdue Libraries exterior photo shows masonry, long repetitive window bands, and a prominent pale vertically framed entrance block.",
                "The model includes repeated glazing and a simple entry portal/canopy, but omits the photo's distinctive pale vertical entry frame and does not establish current entrance location or contemporary facade changes.",
                "The saved preview shows the massing and window rhythm; the entry is not legible from the preview camera angle.",
            ],
            "findings": ["The facade/entrance model is schematic and only partly matched to the archival photograph; the current entrance frontage and bay registration are unverified."],
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 1.5 if is_open and not reopen.get("external_images") else 1.0,
            "max_score": 2,
            "evidence": [
                f"Fresh direct Blender {reopen.get('blender_version')} reopen succeeded with scene {reopen.get('scene')} and collection {reopen.get('collection')}.",
                f"The collection contains {reopen.get('collection_object_count')} mesh objects with no modifiers and no external image dependencies; source snapshots, evidence record, preview, and reopen validation are present.",
                "The manifest declares one object named 'Lilly Hall' and bounds/height that do not match the reopened collection (four objects; 25.055 m shell). This shared metadata discrepancy needs coordinator reconciliation before relying on automatic integration checks.",
            ],
            "findings": ["Manifest object list/count and bounds are stale relative to the asset; collection/scene names themselves match the manifest."],
        },
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    return {
        "building_id": "massing_lilly_hall_e7fc13e",
        "building": "Lilly Hall of Life Sciences",
        "grade_round": "r1",
        "grader": "independent subagent",
        "score": score,
        "max_score": 10,
        "result": "PASS" if score >= 8 else "FAIL",
        "criteria": criteria,
        "evidence": {
            "asset": evidence["asset"],
            "build_script": evidence["build_script"],
            "source_snapshot": "audit/massing_lilly_hall_e7fc13e/sources/purdue_gis_fid_581.json",
            "archival_photo": "audit/massing_lilly_hall_e7fc13e/sources/lilly_hall_archival_exterior.jpg",
            "preview": evidence["geometry_and_validation"]["preview"],
            "reopen_validation": evidence["geometry_and_validation"]["reopen_report"],
            "direct_reopen_performed_by_grader": True,
            "gis_feature": {"FID": attrs.get("FID"), "building_code": attrs.get("BLDG_ABBR"), "ring_vertices": ring_count},
            "max_nearest_vertex_difference_m": max_error,
        },
        "findings": [
            "The exact official GIS plan outline and library packaging validate well, but unverified height/roof and schematic facade limit source fidelity.",
            "Shared modular/manifest metadata is inconsistent with the asset and should be repaired by the coordinator before indexing or integration.",
        ],
    }


if __name__ == "__main__":
    result = evaluate()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
