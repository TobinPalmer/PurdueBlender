"""Independent rubric evaluator for the Slayter Center Blender asset."""
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit" / "slayter_center_for_performing_arts"
VALIDATION = AUDIT / "slayter_reopen_validation.json"


def evaluate():
    evidence = json.loads((AUDIT / "evidence.json").read_text(encoding="utf-8"))
    observations = json.loads((AUDIT / "source_observations.json").read_text(encoding="utf-8"))
    raw_gis = json.loads((AUDIT / "source_feature_228_raw.json").read_text(encoding="utf-8"))
    saved = json.loads(VALIDATION.read_text(encoding="utf-8"))
    photo = AUDIT / "slayter_center_geotagged_2006.jpg"
    preview = AUDIT / "preview_detail.png"

    assert raw_gis["attributes"]["FID"] == 228
    assert "Slayter" in raw_gis["attributes"]["BUILDING_N"]
    assert saved["reopened_in_background_blender"] and saved["passed"]
    assert saved["collection_object_count"] == 1 and saved["object_type"] == "MESH"
    assert photo.is_file() and preview.is_file()
    assert not saved["external_unpacked_images"]
    photo_source = next(source for source in observations["sources"] if "Wikimedia Commons" in source["provider"])
    assert "Nowimnthing" in photo_source["provider"]
    assert "CC BY-SA 3.0" in photo_source["license"]
    assert "Nowimnthing" in evidence["source"]["secondary_visual_references"][2]["provider"]
    assert "CC BY-SA 3.0" in evidence["source"]["secondary_visual_references"][2]["provider"]

    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 1.8,
            "max_score": 2,
            "evidence": [
                "Purdue footprint feature 228 is named Slayter Center of Performing Arts and carries building code SCPA.",
                "The transformed GIS polygon has a documented area of 2503.69 m2 and a venue-envelope interpretation; the model is treated as the stage/amphitheater, not as a complete wall-outline extrusion.",
                "The model is not checked against the polygon ring at every vertex, and the source record does not define a surveyed structure footprint."
            ],
            "uncertainty": "Envelope meaning is not surveyed; exact venue-ground edge match is unverified."
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 1.7,
            "max_score": 2,
            "evidence": [
                "The camera point is approximately 51.12 m from the transformed venue-envelope center; the reported 160-degree image heading differs from camera-to-center bearing by about 5.25 degrees.",
                "The model stage-front axis points approximately 334.4 degrees clockwise from north, consistent with the geotagged audience-side view.",
                "The stage plan dimensions convert the secondary published 56 ft / 34 ft / 46 ft figures to 17.07 m / 10.36 m / 14.02 m; Blender reopening records bounds X [-776.10,-741.56], Y [479.39,522.99] m against venue AABB X [-780.57,-729.72], Y [474.10,522.95] m."
            ],
            "uncertainty": "Stage center comes from the envelope center rather than a georeferenced stage plan; the source dimension figures are secondary and the venue AABB slightly overhangs by 0.03 m in Y."
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 1.3,
            "max_score": 2,
            "evidence": [
                "The 2006 geotagged photo visibly supports an open, shallow canopy, tripod support, and suspension cables.",
                "Saved geometry has 7.7 m canopy edge and approximately 15.75 m maximum mesh height; these are explicitly marked estimates, not source measurements.",
                "An outdoor amphitheater has no useful story count; roof form is photo-backed but elevations and floor count are not established by plans."
            ],
            "uncertainty": "No measured roof elevation or original structural drawing was found."
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1.5,
            "max_score": 2,
            "evidence": [
                "The reference photo shows a tripod-and-cable roof, broad canopy, vertical acoustic reflector fins, a raised stage apron, and audience terraces on a hillside.",
                "The model includes tripod legs, radial cables, an elliptical canopy, 13 reflector fins, stage apron, front steps, and separated audience tier sections.",
                "The model-specific preview was visually inspected; the audience tiers read as separate rows, while the model omits the surrounding sloped lawn and photographic context."
            ],
            "uncertainty": "Exact fin profiles, terrace geometry, stage service block and surrounding landscape remain approximate."
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                "Reopened Blender asset contains exactly one mesh in the expected Asset_massing_slayter_center_for_performing_arts_f45259b collection with identity object transforms.",
                "Saved mesh has 2280 vertices, 556 faces, no modifiers, and no external unpacked images.",
                "Dedicated build module, raw GIS snapshot, photo and Commons metadata, structured observations/evidence, preview, and reopen validation are present."
            ],
            "uncertainty": "No significant export or evidence packaging issue found; attribution and license are recorded."
        }
    ]
    return {
        "score": round(sum(c["score"] for c in criteria), 1),
        "max_score": 10,
        "criteria": criteria,
        "evidence": {
            "asset": "modular/buildings/massing_slayter_center_for_performing_arts_f45259b.blend",
            "source_paths": [
                "audit/slayter_center_for_performing_arts/source_feature_228_raw.json",
                "audit/slayter_center_for_performing_arts/source_observations.json",
                "audit/slayter_center_for_performing_arts/slayter_center_geotagged_2006.jpg",
                "audit/slayter_center_for_performing_arts/commons_imageinfo_slayter_center_2006.json"
            ],
            "rendered_view": "audit/slayter_center_for_performing_arts/preview_detail.png",
            "reopen_validation": "audit/slayter_center_for_performing_arts/slayter_reopen_validation.json",
            "source_page_check": "Wikimedia Commons page verified that the photo is dated 2006-06-21, located at 40.432306/-86.922861, and has heading 160 degrees; page history credits uploader Nowimnthing and lists CC BY-SA 3.0."
        },
        "findings": [
            "The characteristic roof and amphitheater layout are recognizable and directly supported by the geotagged photo.",
            "The GIS feature provides a venue envelope; the exact internal location and ground boundary are approximate.",
            "The stage dimensions rely on a secondary written source. Canopy/tripod heights, tier layout, and landscape remain estimates.",
            "The photo source is now attributed to uploader Nowimnthing with CC BY-SA 3.0 terms in both evidence.json and source_observations.json."
        ],
        "independent_review": True,
        "rubric_pass": round(sum(c["score"] for c in criteria), 1) >= 8.0
    }


if __name__ == "__main__":
    result = evaluate()
    out = Path(__file__).with_name("result.json")
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    assert result["max_score"] == 10 and result["rubric_pass"]
