import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).with_name("independent_grade_r2.json")


def evaluate():
    """Independent evidence review; never treats builder assertions as independently checked facts."""
    base = ROOT / "audit" / "sigma_nu"
    required = [
        base / "sigma_nu_preview.png",
        base / "build_validation.json",
        base / "reopen_validation.json",
        base / "sources" / "source_register.json",
        base / "sources" / "purdue_gis_fid_758.json",
        base / "sources" / "beta_zeta_fall_2019_newsletter_page2_900.jpg",
        base / "sources" / "osm_tower_drive_way_327252145.json",
        ROOT / "modular" / "buildings" / "massing_house_301841330_f58ae87.blend",
        ROOT / "modular" / "buildings" / "build_massing_house_301841330_f58ae87.py",
    ]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    validation = json.loads((base / "reopen_validation.json").read_text(encoding="utf-8"))
    sources = json.loads((base / "sources" / "source_register.json").read_text(encoding="utf-8"))
    gis = json.loads((base / "sources" / "purdue_gis_fid_758.json").read_text(encoding="utf-8"))
    attrs = gis["attributes"]
    newsletter = sources["sources"][1]
    road = sources["sources"][-1]

    # Reopening was attempted via the available Blender connector; it returned
    # "Could not connect to Blender." No local blender.exe or bpy module exists.
    # Therefore the previous builder's reopen_validation is treated as reported
    # evidence only, not an independent pass.
    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2.0,
            "evidence": [
                f"Raw Purdue GIS record FID {attrs['FID']} names {attrs['BUILDING_N']} / {attrs['BLDG_ABBR']} at {attrs['ADDRESS']}; the independent Beta Zeta newsletter photo visibly shows the 1301 address plaque.",
                f"GIS polygon has {validation['source_ring_vertices']} vertices. Builder's saved-file report claims symmetric base-ring vertex error {validation['symmetric_nearest_vertex_error_m']:.8f} m; I could not independently recompute this from Blender geometry.",
                "Visual comparison of the current preview and source photo supports a broad match in building identity and massing footprint, with the GIS polygon treated as a roof/building proxy rather than measured wall line.",
            ],
            "uncertainty": ["No surveyed wall footprint; roof edge offset is unknown."],
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 1.6,
            "max_score": 2.0,
            "evidence": [
                "The saved evidence records the repository's approximate EPSG:4326-to-campus conversion and provides raw GIS and OSM snapshots.",
                "Preview geometry is consistent with the GIS polygon; the reopen report states 0.00003749 m ring error and world bounds, but those Blender values remain builder-reported because a new Blender reopen was unavailable.",
                f"OSM Tower Drive context supports the chosen north/northwest-facing edge only indirectly; source register itself correctly calls the facade bearing an inference ({road['uncertainty']}).",
            ],
            "uncertainty": ["No independent survey/CRS check. The photo is not georeferenced, so front-bearing assignment is still inferred."],
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 0.6,
            "max_score": 2.0,
            "evidence": [
                "The image supports a low, broad, multi-level appearance but supplies no known scale or elevation; the model's 7.2 m wall and 7.45 m top values are estimates.",
                "The GIS NUM_LEVELS=1 and Extrution=44 metadata are undocumented and do not verify storey count or height.",
                "The preview shows a low flat cap; the provided photos do not establish its form or dimensions.",
            ],
            "uncertainty": ["Actual story count, wall height, roof profile, and overall height remain unverified."],
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1.6,
            "max_score": 2.0,
            "evidence": [
                "Fall 2019 newsletter photograph of the address plaque provides direct facade imagery. Its front photo supports brickwork, a broad central entrance zone with light trim, and multiple front openings; the lower side photo supports a projecting bay and red-brick side wall.",
                "The current preview uses subdued red-brown upper brick, a light lower band, two main facade windows, a central opening/canopy, and a restrained side bay. These are broad, defensible generalizations from the visible image.",
                f"Newsletter record explicitly disclaims exact elevations and measurements: {newsletter['uncertainty']}",
            ],
            "uncertainty": ["Exact window count/spacing, sill/lintel details, story split, trim material, and unseen elevations cannot be confirmed; facade bearing is not tied to photo by georeferencing."],
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 1.6,
            "max_score": 2.0,
            "evidence": [
                "Expected .blend, builder script, preview, raw GIS/newsletter/OSM snapshots, and source register are present.",
                f"Builder's reopen record reports expected scene {validation['scene']}, export collection {validation['export_collection']}, {validation['export_collection_object_count']} mesh objects, no modifiers or relative dependencies; these claims could not be independently confirmed with Blender in this review.",
                "Saved validation records geometry bounds and uncertainty; asset appears self-contained from source and render evidence.",
            ],
            "uncertainty": ["Independent load of the final .blend and inspection of collection membership, world matrices, dependencies, and evaluated meshes could not be performed in this environment."],
        },
    ]
    score = round(sum(c["score"] for c in criteria), 1)
    result = {
        "building_id": "massing_house_301841330_f58ae87",
        "grader": "independent_grader_r2",
        "grade_round": 2,
        "score": score,
        "max_score": 10,
        "passing_threshold": 8,
        "passed": score >= 8,
        "criteria": criteria,
        "evidence": {
            "asset": "modular/buildings/massing_house_301841330_f58ae87.blend",
            "builder_script": "modular/buildings/build_massing_house_301841330_f58ae87.py",
            "preview": "audit/sigma_nu/sigma_nu_preview.png",
            "source_register": "audit/sigma_nu/sources/source_register.json",
            "raw_gis": "audit/sigma_nu/sources/purdue_gis_fid_758.json",
            "newsletter_photo": "audit/sigma_nu/sources/beta_zeta_fall_2019_newsletter_page2_900.jpg",
            "road_context": "audit/sigma_nu/sources/osm_tower_drive_way_327252145.json",
            "builder_reopen_record": validation,
            "independent_fresh_reopen": {
                "attempted": True,
                "completed": False,
                "reason": "Blender connector reported it could not connect to Blender; no local blender.exe or bpy Python module was available.",
            },
            "missing_required_files": missing,
        },
        "findings": [
            "Score is below the 8/10 threshold. The current iteration improves the previously criticized facade generalization: broad brick/light-masonry contrast and the entrance/bay now align with visible newsletter imagery, with fewer unsupported openings.",
            "Most limiting criterion is height/floors/roof (0.6/2): current sources do not establish story count, heights, or roof silhouette. Find measured elevation/assessor imagery with an exact parcel match, or continue to mark these as provisional estimates.",
            "Independent Blender reopen was unavailable, so all numerical mesh/export properties from reopen_validation.json are reported builder evidence, not independently reproduced checks. A reviewer with Blender access should freshly load the exact saved asset before sign-off.",
            "The GIS ring is an excellent reported plan-shape match but remains a building/roof polygon proxy; facade bearing is contextual inference only.",
        ],
    }
    return result


if __name__ == "__main__":
    result = evaluate()
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
