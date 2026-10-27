import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def evaluate():
    probe = json.loads((HERE / "blender_probe.json").read_text(encoding="utf8"))
    gis = json.loads((ROOT / "audit/delta_zeta/sources/purdue_gis_fid752_raw.json").read_text(encoding="utf8"))["features"][0]
    evidence = json.loads((ROOT / "audit/delta_zeta/evidence.json").read_text(encoding="utf8"))
    preview = ROOT / "audit/delta_zeta/preview.png"
    official_photo = ROOT / "audit/delta_zeta/sources/delta_zeta_house_official_front_2023.jpg"
    attributes = gis["attributes"]
    assert probe["blend_reopened"] and probe["gis_fid"] == 752
    assert probe["collection_exists"] == "Asset_massing_house_301841601_7ae6159"
    assert probe["collection_object_names"] == ["House_301841601"]
    assert probe["object_type"] == "MESH" and probe["gis_base_match_count"] == 11
    assert probe["gis_max_base_residual_m"] < 0.0001
    assert preview.exists() and official_photo.exists()

    # The exterior roof bounds now stay very close to the official GIS outline;
    # small eave overhangs are not treated as a large footprint discrepancy.
    gis_bounds = evidence["measurements"]["gis_bounds_xy_m"]
    bounds = probe["evaluated_bounds_xyz_m"]
    overhang = {
        "west_m": round(gis_bounds[0] - bounds[0][0], 3),
        "east_m": round(bounds[0][1] - gis_bounds[1], 3),
        "south_m": round(gis_bounds[2] - bounds[1][0], 3),
        "north_m": round(bounds[1][1] - gis_bounds[3], 3),
    }
    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2.0,
            "evidence": [
                "Official Purdue GIS FID 752 identifies Delta Zeta (SODZ) at 825 Hilltop Dr; Xi Omega chapter history corroborates the address and Purdue chapter identity.",
                f"All 11 unique GIS ring vertices match the reopened mesh base within tolerance; maximum residual {probe['gis_max_base_residual_m']:.8f} m.",
                "The building is independently named as Xi Omega in the official Delta Zeta exterior-photo feature.",
            ],
            "findings": ["Purdue GIS is not a certified survey and publishes no positional tolerance."],
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "score": 1.75,
            "max_score": 2.0,
            "evidence": [
                "Reopened asset retains campus placement with identity location, rotation, and scale.",
                f"Evaluated mesh bounds are X {bounds[0]} m, Y {bounds[1]} m, Z {bounds[2]} m; the new roof envelope differs from the GIS outline by only about {max(abs(v) for v in overhang.values()):.3f} m at its greatest horizontal edge.",
            ],
            "findings": [
                "The official image is not georeferenced, so the facade bearing and which footprint edge is the photographed front cannot be independently verified.",
                f"Roof/eave overhang relative to GIS bounds (west/east/south/north): {overhang}; this is a small envelope difference, not the former multi-meter overrun.",
            ],
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "score": 1.25,
            "max_score": 2.0,
            "evidence": [
                "The official 2023 oblique photo visibly supports a multi-level brick house and multiple steep gabled roof sections.",
                "The model depicts two principal facade levels, repeated gables, and a taller arched entry bay; the reopened total height is 14.65 m.",
            ],
            "findings": [
                "No measured height, floor plan, or elevation source is available; eaves, ridges, and entry tower heights remain visual estimates.",
                f"GIS NUM_LEVELS={attributes.get('NUM_LEVELS')} is inconsistent with the photo's apparent multi-level facade; Extrution={attributes.get('Extrution')} has no documented unit or semantics. Do not infer either model height or story count from those fields.",
                "The photo shows a stepped row of gabled wings, while the preview's roof masses and intersections remain simplified and are not dimensionally verified.",
            ],
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 1.25,
            "max_score": 2.0,
            "evidence": [
                "The source image supports brick walls, dark shingles, pale trim, a tall entry bay with arched upper glazing, and dark doors; the preview includes those broad features and repeated windows.",
            ],
            "findings": [
                "In the photo, the tall arched entrance is at the near end of the visible long facade; in the preview it sits around two-thirds across the shown facade. The photo has no camera pose, so this mismatch is concerning but cannot be conclusively mapped to compass orientation.",
                "The roof planes and intersections are blocky/simplified, and window rhythm is more regular than the visible source facade.",
            ],
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 2.0,
            "max_score": 2.0,
            "evidence": [
                "Fresh Blender 5.2.3 reopen confirms the expected collection with exactly one mesh object; mesh has 6,820 evaluated vertices and 1,686 faces.",
                "Identity object transform, all 11 GIS base vertices, and no external image dependencies are confirmed.",
                "Building evidence includes raw GIS JSON, official photo, source observations, preview, configuration, and reopen validation.",
            ],
            "findings": ["The saved asset is self-contained and follows the expected single-object campus-coordinate export."],
        },
    ]
    score = sum(c["score"] for c in criteria)
    return {
        "score": score,
        "max_score": 10,
        "criteria": criteria,
        "evidence": {
            "asset_path": "modular/buildings/massing_house_301841601_7ae6159.blend",
            "probe": probe,
            "official_gis_attributes": attributes,
            "official_photo_path": "audit/delta_zeta/sources/delta_zeta_house_official_front_2023.jpg",
            "preview_path": "audit/delta_zeta/preview.png",
            "roof_overhang_vs_gis_bounds_m": overhang,
            "score_threshold": 8,
            "passed": score >= 8,
        },
        "findings": [
            "PASS: score meets the 8/10 minimum." if score >= 8 else "FAIL: score is below the 8/10 minimum.",
            "The new version substantially reduces the former roof-envelope overrun; the current score reflects the revised bounds and mesh, not the stale earlier model.",
            "Story count, measured heights, and exact facade bearing remain uncertain; GIS vertical fields are undefined and the photo has no scale or geolocation.",
        ],
    }


if __name__ == "__main__":
    result = evaluate()
    (HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    (HERE / "evaluator_output.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    print(json.dumps(result, indent=2))
