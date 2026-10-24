"""Independent R3 scorecard for John T. McCutcheon Residence Hall.

Scores are reviewer judgments against the project's five 2-point criteria.
This evaluator reads no model data and does not modify the building asset.
"""

import json
from pathlib import Path


def evaluate():
    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 1.9,
            "max_score": 2.0,
            "evidence": "Official Purdue Residences pages identify McCutcheon Hall. GIS FeatureServer FID 57 matches the transformed base-plinth AABB to under 0.0001 m at recorded precision.",
            "findings": "Strong identity and envelope registration. The GIS layer is not survey control and the AABB match alone does not verify every structural wall or the complete footprint shape.",
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 1.6,
            "max_score": 2.0,
            "evidence": "The asset uses the documented approximate local tangent-plane transform; GIS bounds and modeled plinth bounds align. The source records the minimum-rotated rectangle and polygon rings.",
            "findings": "No R3 master-placement check was performed. The local transform is approximate, and full structural outline, compass-facing facade assignment, and measured dimensions are not independently established.",
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 0.9,
            "max_score": 2.0,
            "evidence": "The model visibly represents two tall wings, a lower connector, rooftop mechanical equipment, and roof enclosures. R3 documentation correctly labels the 30.35 m modeled top and GIS ten-level attribute unverified.",
            "findings": "No measured elevation, verified story count, or direction-registered full-building image resolves the modeled height, floor spacing, or roof/penthouse form. The oblique official photo only shows some rooftop equipment.",
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1.45,
            "max_score": 2.0,
            "evidence": "Purdue Residences' official exterior photo supports qualitative red brick, blue-gray glazing, a perforated concrete-block screen near the low glazed entry, light base, wall sign, and roof-level mechanical equipment. These categories are visible in the saved entrance render.",
            "findings": "The reference is cropped, oblique, and not direction-identified, so it cannot verify dimensions or exact local placement. The hero shows extensive blank wall areas and simplified repeated window groups; other elevations and opening cadence remain unverified.",
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 1.8,
            "max_score": 2.0,
            "evidence": "Blender 5.2.3 reopened the saved asset; expected collection and root transform are intact; 10 foliage textures are packed; no unresolved unpacked image dependencies; hero and entrance renders were produced; GIS overlay is render-hidden and viewport-visible.",
            "findings": "Validation is strong for standalone asset integrity. R3 does not validate master-scene placement or add an as-built interior; the existing interior shells remain explicitly unverified.",
        },
    ]
    score = sum(item["score"] for item in criteria)
    return {
        "building": "John T. McCutcheon Residence Hall",
        "building_id": "mccutcheon_hall",
        "revision_reviewed": 3,
        "review_date": "2026-10-24",
        "review_type": "independent_full_building_read_only",
        "score": round(score, 2),
        "score_display": round(score, 1),
        "max_score": 10,
        "acceptance_threshold": 8.0,
        "meets_threshold": score >= 8.0,
        "criteria": criteria,
        "evidence": [
            {"title": "Purdue University Residences — McCutcheon", "url": "https://www.housing.purdue.edu/my-housing/options/residence-halls/mccutcheon.html", "use": "Identity, residence hall program, opening date, shared bathroom/common-space amenities; not a measured plan or elevation."},
            {"title": "Purdue University Residences — accommodations exterior photo", "url": "https://www.housing.purdue.edu/visit/conferences/accommodations.html", "image_url": "https://www.housing.purdue.edu/images/_hero/mccutcheon-exterior-640x360.jpg", "use": "Qualitative entrance/facade feature comparison only; cropped, oblique, undated, unscaled, and not direction-identified."},
            {"title": "Purdue BuildingShapesZip4 FeatureServer layer 0, FID 57", "url": "https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0", "use": "GIS footprint-envelope comparison using the retained project snapshot; approximate transform, not survey control."},
            {"title": "Purdue News Service photo finding aid MSP19", "url": "https://archives.lib.purdue.edu/fa/MSP19_News_Service.pdf", "use": "Confirms archival photo holdings, but catalog entries were not used to infer geometry."},
        ],
        "reviewed_files": [
            "modular/buildings/mccutcheon_hall.blend",
            "audit/mccutcheon_hall/REVIEW_R3.md",
            "audit/mccutcheon_hall/mccutcheon_r3_evidence.json",
            "audit/mccutcheon_hall/mccutcheon_r3_validation.json",
            "audit/mccutcheon_hall/mccutcheon_r3_hero.png",
            "audit/mccutcheon_hall/mccutcheon_r3_entrance.png",
            "audit/mccutcheon_hall/gis_fid57_snapshot.json",
        ],
        "limitations": [
            "No metric height, verified floor count, measured roof form, or as-built interior/circulation plan is established by the cited evidence.",
            "R3 is a presentation revision; it makes no building-geometry changes.",
            "The GIS comparison verifies a local envelope registration, not survey-accurate wall geometry or master placement.",
        ],
        "read_only_review": True,
        "asset_edited": False,
        "master_edited": False,
        "shared_index_edited": False,
    }


if __name__ == "__main__":
    result = evaluate()
    output = Path(__file__).with_name("independent_review_r3_scorecard.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"score": result["score"], "score_display": result["score_display"], "meets_threshold": result["meets_threshold"], "output": str(output)}, indent=2))
