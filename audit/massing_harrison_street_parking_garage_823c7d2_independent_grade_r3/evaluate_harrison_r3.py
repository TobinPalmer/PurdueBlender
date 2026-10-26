"""Independent r3 evaluation for Harrison Street Parking Garage.

Scores the saved asset against AGENT.md using a fresh read-only Blender reopen,
archived official GIS, archived aerial, source record, and saved rendered views.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def evaluate():
    reopened = json.loads((HERE / "direct_reopen_inspection.json").read_text(encoding="utf-8"))
    source = json.loads((ROOT / "audit/massing_harrison_street_parking_garage_823c7d2/source_record.json").read_text(encoding="utf-8"))
    validation = json.loads((ROOT / "audit/massing_harrison_street_parking_garage_823c7d2/validation.json").read_text(encoding="utf-8"))
    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2,
            "evidence": "Purdue GIS FID 892 identifies BLDG_ABBR PGH, Harrison Street Parking Garage, 719 Clinic Drive. The raw GIS ring is the deck outline after the repository's documented local transform. The archived Indiana aerial depicts the same long, indented roof plan in this site context.",
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "score": 1.8,
            "max_score": 2,
            "evidence": "Fresh Blender 4.5.15 read-only reopen found the structural slabs at X [-361.5203,-303.2453] m and Y [-747.1450,-662.7343] m, matching the transformed GIS bounds to rounding. The full object bounds are X [-361.7581,-302.9874], Y [-747.3728,-662.5153], only about 0.24 m beyond the GIS shell at maximum. Orientation follows the source ring; no separate polygon IoU metric is supplied.",
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "score": 1.6,
            "max_score": 2,
            "evidence": "WGI supports six total levels including one below grade. The current asset has six structural deck slabs and a roof deck, with 3.2 m intervals and 17.1 m screen top identified as estimates. Unlike the prior revision, the roof render now includes parking-stall striping, circulation arrows, a raised central open-sided canopy with four piers, and a smaller edge enclosure corresponding to features visible in the archived orthophoto. Exact stall layout, canopy dimensions/function, ramp geometry, floor-to-floor heights, and roof/screen elevation remain unverified.",
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 1.3,
            "max_score": 2,
            "evidence": "WGI and contractor evidence summarized in the source record support a cast-in-place garage with brick veneer, architectural precast, and perimeter planting. The oblique and elevation renders show repeated open parking bays, concrete piers/spandrels, a brick service core, screen, and planter curbs. There are no dimensioned elevations; bay rhythm, core placement, entrance locations, and facade proportions remain interpretive, and an entrance/ramp sequence is not clearly represented.",
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 1.5,
            "max_score": 2,
            "evidence": "Fresh reopen found the expected stable scene and collection with 549 mesh objects, no non-mesh collection objects, no linked libraries, and no file-backed image dependencies. Source snapshots, metadata, build notes, validation JSON/log, and three views are present. Blender 4.5.15 opened the Blender 5.2-authored file for inspection but reported the newer writer version; the massing and portability checks passed, with cross-version editing/render compatibility still a limitation.",
        },
    ]
    result = {
        "score": round(sum(c["score"] for c in criteria), 1),
        "max_score": 10,
        "criteria": criteria,
        "evidence": {
            "asset": reopened["asset"],
            "scene": reopened["scene_names"],
            "collection": reopened["expected_collection"],
            "direct_reopen_tool": "Blender 4.5.15 LTS, read-only fresh open; file header reports Blender 5.2 writer",
            "direct_reopen_object_count": reopened["object_count"],
            "direct_reopen_mesh_object_count": reopened["mesh_objects"],
            "direct_reopen_bounds_xyz_m": reopened["bounds_xyz"],
            "validation_structural_deck_bounds_xyz_m": validation["structural_deck_bounds_xyz_m"],
            "sources": [{"provider": s["provider"], "feature": s["feature"], "url": s["url"]} for s in source["sources"]],
            "reviewed_views": [
                "audit/massing_harrison_street_parking_garage_823c7d2/renders/harrison_oblique_review.png",
                "audit/massing_harrison_street_parking_garage_823c7d2/renders/harrison_elevation_review.png",
                "audit/massing_harrison_street_parking_garage_823c7d2/renders/harrison_roof_review.png",
            ],
            "reviewed_roof_source": "audit/massing_harrison_street_parking_garage_823c7d2/roof_aerial_zoom.png, derived from archived sources/current_aerial_harrison_crop.jpg",
            "gis_feature": "Purdue BuildingShapesZip4 FID 892 / BLDG_ABBR PGH",
        },
        "findings": [
            "Passes the repository 8/10 threshold at 8.2/10. The revised roof treatment now responds to visible aerial evidence for rooftop parking, circulation arrows, and a raised central structure/open-sided area.",
            "Deck outline and campus position closely match the transformed Purdue GIS footprint. Full object bounds extend about 0.24 m beyond the ring because edge-spaced facade features cross the structural perimeter slightly.",
            "Six levels including one below grade are sourced; story spacing and overall height remain estimates because neither GIS vertical-field units nor dimensioned elevations are available.",
            "Facade materials are qualitatively sourced, but entrance/ramp access, bay dimensions, core location, canopy dimensions/function, and exact rooftop stall arrangement remain inferred or unverified.",
            "Blender 4.5.15 reopened the 5.2-authored asset for read-only geometry inspection and reported its newer file version. The saved library is self-contained, though same-version rebuild/render remains the safer compatibility path.",
        ],
        "independent_review": True,
        "read_only_asset_source_shared_index": True,
    }
    assert result["max_score"] == 10
    assert abs(result["score"] - sum(c["score"] for c in criteria)) < 1e-9
    return result


if __name__ == "__main__":
    result = evaluate()
    (HERE / "grade_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
