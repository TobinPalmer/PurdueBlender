"""Independent rubric evaluation for the Honors College South asset."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
AUDIT = ROOT / "audit" / "honors_college_residences_south_c663781"
EXPECTED_SHA256 = "882c6933ef2dd37e84cf9eaadbbbfafdd7b30b724fbf55e0a25f440d68bf1a64"


def evaluate():
    audit = json.loads((HERE / "reopen_audit.json").read_text(encoding="utf-8"))
    feature = json.loads((AUDIT / "sources" / "purdue_gis_fid905.json").read_text(encoding="utf-8"))["feature"]
    source_record = json.loads((AUDIT / "source_record.json").read_text(encoding="utf-8"))
    validation = json.loads((AUDIT / "validation.json").read_text(encoding="utf-8"))

    assert audit["sha256"] == EXPECTED_SHA256 == validation["asset_sha256"]
    assert feature["attributes"]["FID"] == 905
    assert feature["attributes"]["BLDG_ABBR"] == "HCRS"
    assert feature["attributes"]["BUILDING_N"] == "Honors College Residence Hall South"
    assert feature["attributes"]["ADDRESS"] == "1101 3rd Street"
    assert audit["scene_name_matches"] and audit["export_collection_found"]
    assert audit["collection_direct_scene_membership"]
    assert len(audit["footprint_comparisons"]) == 1
    fp = audit["footprint_comparisons"][0]
    assert fp["source_vertex_count"] == 36 and fp["model_unique_xy_count"] == 36
    assert fp["source_to_model_max_nearest_m"] < 0.001
    assert fp["model_to_source_max_nearest_m"] < 0.001
    assert audit["linked_libraries"] == [] and audit["file_images"] == []

    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2.0,
            "evidence": [
                "Raw Purdue BuildingShapes feature 905 identifies HCRS, Honors College Residence Hall South, 1101 3rd Street.",
                "Independently transformed all 36 outer-ring vertices from the saved EPSG:3857 feature into the project campus coordinate frame and compared them with the reopened model shell; the maximum symmetric nearest-vertex residual is about 0.000016 m.",
                "Official Purdue Residences identifies North/Lee-Such Tower and South Tower as distinct buildings in this complex."
            ],
            "limitations": ["The Purdue GIS record does not establish a survey-grade wall boundary or reliable capture date; source uncertainty is recorded by the builder."]
        },
        {
            "criterion": "Position, orientation, scale, and dimensions",
            "score": 2.0,
            "max_score": 2.0,
            "evidence": [
                "A fresh Blender 5.2.3 reopen confirms that the evaluated shell vertices match the complete source ring after applying the documented transform, including its setbacks and orientation.",
                "The model and source bounds agree at approximately 25.67 m east-west by 92.29 m north-south, within mesh float precision.",
                "The saved massing geometry is in the expected campus-world coordinate frame and its asset collection is present in its scene."
            ],
            "limitations": ["The project conversion from WGS84 into local XY is approximate and should not be interpreted as surveyed geodesy."]
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "score": 1.25,
            "max_score": 2.0,
            "evidence": [
                "Purdue's current building-information page states six stories plus a basement; the first floor is academic and floors two through six are residential. The modeled shell is divided into that six-level arrangement, with the interior basement context labeled schematic.",
                "The reopened model reaches 19.90 m at the shell eave and 22.90 m at the south gable. The facade and roof elevations are estimates, not measured values.",
                "The raw GIS contains NUM_LEVELS=8, CountOfFLO=8, and Extrution=96 without a documented height unit; the model record correctly discloses this conflict with the official story description."
            ],
            "limitations": ["No reliable source measures the South building's roof/eave height. The gable form is inferred from a complex-wide 2016 image, not independently documented as South-specific."]
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 1.25,
            "max_score": 2.0,
            "evidence": [
                "The saved preview and reopened model contain red-brown brick, repeated framed windows, pale story/precast articulation, a glazed atrium/entry element, and a dark roof—features visible in the retained Purdue 2016 exterior photograph.",
                "The exterior source image depicts the Honors College and Residences project but is not labeled as a South-only view. The builder explicitly identifies the attribution of the glazed gable/entry composition to South as an inference.",
                "The rendered review view shows the principal forms and repeated facade rhythm, while the model's limited project-specific source means fine facade and entrance placement cannot be independently confirmed."
            ],
            "limitations": ["No South-specific dimensioned elevation or clear street-level photograph is included; facades, entrance orientation, window rhythm, and roof articulation remain partly interpretive."]
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 2.0,
            "max_score": 2.0,
            "evidence": [
                "The file SHA-256 matches the frozen reviewed revision. Fresh reopen finds the expected scene and named asset collection with 149 mesh objects.",
                "No linked Blender libraries or external image files are referenced; the asset uses procedural materials.",
                "The building audit includes raw GIS and layer metadata, official source snapshots, source record, validation script/result, and exterior preview. Interior objects are explicitly labeled schematic/not-as-built."
            ],
            "limitations": []
        }
    ]
    result = {
        "building": "Honors College and Residences South",
        "asset_path": audit["asset_path"],
        "asset_sha256": audit["sha256"],
        "grader": "Independent source and fresh-open geometry audit",
        "status": "PASS" if sum(c["score"] for c in criteria) >= 8 else "NEEDS_REVISION",
        "score": round(sum(c["score"] for c in criteria), 2),
        "max_score": 10,
        "criteria": criteria,
        "evidence": {
            "reopened_asset": "reopen_audit.json",
            "source_record": "../source_record.json",
            "builder_validation": "../validation.json (cross-check only; evaluator recomputed the footprint comparison independently)",
            "raw_gis_feature": "../sources/purdue_gis_fid905.json",
            "preview": "../hcrs_south_exterior_review.png",
            "source_urls": [
                "https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/905?f=pjson",
                "https://www.housing.purdue.edu/my-housing/options/residence-halls/honors-college.html",
                "https://www.honors.purdue.edu/admissions/building-info.php",
                "https://frpinc.com/projects/honors-college-residences/",
                "https://www.purdue.edu/uns/images/2016/pt-honors-collegeLO.jpg"
            ],
            "independent_web_checks": [
                "Purdue Honors College Building Information says the complex is six stories plus a basement, with an academic first floor and residential floors two through six.",
                "Purdue Residences identifies Lee-Such Tower (formerly North Tower) and South Tower as distinct parts of the complex and gives the 1101 Third Street address.",
                "Fink Roberts & Petrie's project page describes five residential floors above the first-level academic/support program and a cast-in-place concrete podium; this page is project-wide rather than South-specific."
            ]
        },
        "findings": [
            "The source-derived plan location, orientation, and complete 36-vertex footprint are unusually strong and independently verified.",
            "The correct floor count is supported by Purdue, but height is estimated and the source GIS level/extrusion fields conflict or lack a documented unit.",
            "Brick, glazing, and window patterns are consistent with the complex-wide Purdue photo. The South-specific gable/entry assignment and detailed facade composition remain uncertain; no surveyed or South-specific elevation was found.",
            "The schematic interior is useful for visual context but has no as-built room-layout evidence; it is correctly labeled and receives no claim of as-built accuracy."
        ]
    }
    return result


if __name__ == "__main__":
    result = evaluate()
    (HERE / "grade_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"score": result["score"], "max_score": result["max_score"], "status": result["status"]}, indent=2))

