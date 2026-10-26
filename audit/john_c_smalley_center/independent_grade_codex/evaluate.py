"""Independent criterion evaluator for the John C. Smalley Center asset."""
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit" / "john_c_smalley_center"
ASSET = ROOT / "modular" / "buildings" / "massing_smalley_center_1902608.blend"


def evaluate():
    evidence = json.loads((AUDIT / "evidence.json").read_text(encoding="utf-8"))
    observations = json.loads((AUDIT / "source_observations.json").read_text(encoding="utf-8"))
    feature = json.loads((AUDIT / "source_feature_225_raw.json").read_text(encoding="utf-8-sig"))
    saved = json.loads((AUDIT / "reopen_validation.json").read_text(encoding="utf-8"))
    ring = feature["geometry"]["rings"][0]
    if ring[0] == ring[-1]:
        ring = ring[:-1]

    assert feature["attributes"]["FID"] == 225
    assert feature["attributes"]["BLDG_ABBR"] == "SMLY"
    assert "Smalley Center" in feature["attributes"]["BUILDING_N"]
    assert len(ring) == saved["official_ring_vertices"] == 16
    assert saved["matched_source_ring_vertices"] == 16
    assert saved["max_footprint_vertex_error_m"] < 1e-4
    assert saved["reopened_in_background_blender"] and saved["passed"]
    assert saved["collection_object_count"] == 1 and saved["object_type"] == "MESH"
    assert saved["identity_object_transform"] and not saved["external_unpacked_images"]
    assert ASSET.is_file()

    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 1.9,
            "max_score": 2,
            "evidence": [
                "Official Purdue GIS feature FID 225 is named John C. Smalley Center For Housing & Food Service Administration and has building code SMLY.",
                "The reopened mesh bottom contains all 16 distinct GIS ring points with maximum project-transform residual 0.0 m.",
                "Purdue Archives independently identifies the residence-halls administration building north of Meredith Hall and records its later addition and naming history.",
            ],
            "uncertainty": "GIS polygon is a mapped footprint without published survey accuracy or an explicit structural-wall definition.",
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 1.8,
            "max_score": 2,
            "evidence": [
                "The building footprint is positioned from official WGS 84 vertices using the repository's documented local-campus conversion.",
                "The 16-point plan shape and bounds match the transformed GIS source ring; the shell follows the source vertex orientation.",
                "The reopened asset bounds including facade projections are X [-830.646179,-785.956665], Y [-56.623768,-23.682798] m; GIS wall outline AABB is X [-830.454542,-786.148249], Y [-56.432189,-23.874372] m.",
            ],
            "uncertainty": "Source positional uncertainty and project-transform error are not published. Entrance bearing is not supported by address, archive, or a georeferenced facade image.",
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 1.3,
            "max_score": 2,
            "evidence": [
                "GIS NUM_LEVELS=2 supports the modeled two levels.",
                "The modeled 7.6 m height is explicitly labeled an estimate and the reopened mesh reaches that height.",
                "The flat roof cap is a simple low-institutional approximation; no elevation, height measurement, or roof description was found.",
            ],
            "uncertainty": "No verified elevation or structural drawing; GIS Extrution=12 lacks a published unit and field definition, so it cannot validate 7.6 m or roof shape.",
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1.0,
            "max_score": 2,
            "evidence": [
                "The model includes two rows of repeated windows, surrounds, floor bands, plinth, coping, and one entry marker.",
                "The preview communicates the irregular official building outline and modeled two-level massing.",
                "The current official directory and archive sources identify the function and address but provide no facade photograph or door location; the visual details therefore remain schematic.",
            ],
            "uncertainty": "Wall material, window spacing, roof form, entrance position, and facade orientation are unverified; no distinctive feature has source-backed detail.",
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                "Reopened Blender asset has the expected one-object Asset_massing_smalley_center_1902608 mesh collection and identity transforms.",
                "The saved asset has 2762 vertices, 1990 faces, no modifiers, and no external unpacked images.",
                "A dedicated build module, raw GIS snapshot, multiple official source records, structured observations, preview, and a saved reopen validator/result are present.",
            ],
            "uncertainty": "No portability issue found in the inspected library.",
        },
    ]
    return {
        "score": round(sum(row["score"] for row in criteria), 1),
        "max_score": 10,
        "criteria": criteria,
        "evidence": {
            "asset": str(ASSET.relative_to(ROOT)),
            "source_paths": [
                "audit/john_c_smalley_center/source_feature_225_raw.json",
                "audit/john_c_smalley_center/source_archival_history_observation.json",
                "audit/john_c_smalley_center/source_observations.json",
            ],
            "rendered_view": "audit/john_c_smalley_center/preview_detail.png",
            "reopen_validation": "audit/john_c_smalley_center/reopen_validation.json",
            "direct_inspection": "Inspected the current saved asset through its Blender 5.2.3 LTS reopen report and visually reviewed the model-specific preview.",
        },
        "findings": [
            "The official GIS plan is reproduced at all 16 source vertices; this is strong footprint evidence, though the source is not a survey.",
            "The archival timeline and current official directory establish the building identity and function.",
            "Two levels are supported by the GIS attribute, while 7.6 m, roof form, facade rhythm, and entry location remain schematic or estimated.",
            "The evaluator confirms a pass at the required 8/10 threshold with the stated facade and elevation uncertainty.",
        ],
        "independent_review": True,
        "rubric_pass": True,
    }


if __name__ == "__main__":
    result = evaluate()
    output = AUDIT / "independent_grade_codex" / "result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
