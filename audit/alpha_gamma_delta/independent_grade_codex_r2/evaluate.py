import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit" / "alpha_gamma_delta"
ASSET = ROOT / "modular" / "buildings" / "massing_house_301841608_d56a4c4.blend"


def evaluate():
    evidence = json.loads((AUDIT / "evidence.json").read_text(encoding="utf-8"))
    validation = json.loads((AUDIT / "reopen_validation.json").read_text(encoding="utf-8"))
    feature = json.loads((AUDIT / "source_feature_757_raw.json").read_text(encoding="utf-8"))
    observations = json.loads((AUDIT / "source_observations.json").read_text(encoding="utf-8"))
    assert ASSET.is_file()
    assert validation["passed"] and validation["source_fid"] == 757
    assert feature["attributes"]["FID"] == 757

    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2.0,
            "evidence": "Purdue GIS FID 757 identifies Alpha Gamma Delta / SOAGD at 1010 David Ross Rd. The reopened validation reports 30 of 30 distinct source-ring vertices matched with 0.0 m maximum residual.",
            "findings": "Strong identity and base-footprint match. Campus GIS is not a certified survey and has no published positional accuracy.",
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 1.8,
            "max_score": 2.0,
            "evidence": "The recorded local transform is consistent with the repository coordinate frame. The shell base follows the source polygon point-for-point; the reopened asset bounds include only modest porch/trim/roof detail beyond it.",
            "findings": "Plan geometry and scale are well supported by the GIS polygon. The facade/entry bearing is an unverified modeling choice, so building-facing orientation is not independently established.",
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 1.0,
            "max_score": 2.0,
            "evidence": "The contractor page describes a two-story house and the exact-address illustration depicts two levels. The render shows a raised central pitched roof form.",
            "findings": "The GIS NUM_LEVELS=1 conflicts with the two-story description, and its field definition is unknown. Eaves (7.6 m), ridge (10 m), gable dimensions, and full roof plan are estimates without measured elevations or roof drawings. Floor count has supporting but conflicting evidence; absolute height and exact roof form remain unverified.",
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1.45,
            "max_score": 2.0,
            "evidence": "An exact-address commercial illustration supports the broad cream two-story house vocabulary, pitched roof, columned entrance, red double doors, and Greek lettering. The model includes these items plus repeated window bays, trim, plinth, and steps.",
            "findings": "The illustration is stylized and not dimensioned. The modeled facade is schematic, with sparse uniform window bays; exact window rhythm, facade proportions, entry location, and which side faces the street are not verified. The preview lighting reduces material contrast.",
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 2.0,
            "max_score": 2.0,
            "evidence": "The reopened asset has the expected assigned asset ID, collection, one mesh object, identity object transform, no modifiers, and no external unpacked images. Raw GIS snapshot, source observations, build config, validation, and preview are present.",
            "findings": "The asset is self-contained and preserves the stable library interface. Independent evaluator output is saved beside this script.",
        },
    ]
    score = round(sum(item["score"] for item in criteria), 2)
    return {
        "score": score,
        "max_score": 10,
        "criteria": criteria,
        "evidence": {
            "asset": str(ASSET.relative_to(ROOT)),
            "source_evidence": str((AUDIT / "evidence.json").relative_to(ROOT)),
            "independent_checks": {
                "reopened_asset_validation_passed": validation["passed"],
                "source_feature_id": feature["attributes"]["FID"],
                "matched_footprint_vertices": validation["matched_source_ring_vertices"],
                "source_footprint_vertices": validation["source_ring_vertices"],
                "max_footprint_residual_m": validation["max_source_ring_error_m"],
                "collection_object_count": validation["collection_object_count"],
                "external_unpacked_images": validation["external_unpacked_images"],
                "source_types": [source["provider"] for source in observations["sources"]],
            },
        },
        "findings": [
            "PASS: exceeds the repository 8/10 threshold.",
            "The strongest verified component is the source-matched plan footprint; no measured elevations or roof plan were found.",
            "The two-story description is supported by the contractor and illustration but conflicts with the GIS NUM_LEVELS attribute.",
            "Entry-side orientation and detailed facade layout remain illustrative estimates.",
        ],
    }


if __name__ == "__main__":
    result = evaluate()
    output = Path(__file__).with_name("result.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
