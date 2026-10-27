import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROBE = json.loads((HERE / "blender_probe.json").read_text(encoding="utf-8"))
GIS = json.loads((ROOT / "audit/sigma_kappa/sources/purdue_gis_fid780_raw.json").read_text(encoding="utf-8-sig"))["features"][0]
OBS = json.loads((ROOT / "audit/sigma_kappa/source_observations.json").read_text(encoding="utf-8"))


def evaluate():
    attributes = GIS["attributes"]
    gis_match = (
        attributes["FID"] == 780
        and attributes["BUILDING_N"] == "Sigma Kappa"
        and attributes["ADDRESS"] == "427 Russell St"
        and PROBE["gis_fid"] == 780
        and PROBE["gis_base_match_count"] == 21
        and PROBE["gis_max_base_residual_m"] <= 0.0001
    )
    identity_transform = (
        all(abs(v) < 1e-7 for v in PROBE["object_location"])
        and all(abs(v) < 1e-7 for v in PROBE["object_rotation_euler"])
        and all(abs(v-1.0) < 1e-7 for v in PROBE["object_scale"])
    )
    single_expected_mesh = (
        PROBE["collection_objects"] == ["House_301840869"]
        and PROBE["scene_objects"] == [["House_301840869", "MESH"]]
    )
    portable = PROBE["blend_reopened"] and single_expected_mesh and not PROBE["external_image_paths"]
    source_images_present = all((ROOT / "audit/sigma_kappa" / p).exists() for p in [
        "sources/two_tulips_house_illustration.jpg",
        "sources/sigma_kappa_2023_newsletter_page0.jpg",
    ])

    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "score": 2.0 if gis_match else 0.0,
            "max_score": 2.0,
            "evidence": [
                "Official Purdue GIS FID 780 labels the feature Sigma Kappa (SOSK) at 427 Russell St.",
                "The 2023 Beta Sigma newsletter says 427 Russell Street is the chapter house; Purdue Panhellenic identifies Sigma Kappa as Beta Sigma.",
                f"Fresh Blender probe matched {PROBE['gis_base_match_count']}/21 unique GIS vertices; maximum base residual {PROBE['gis_max_base_residual_m']:.8f} m.",
            ],
            "findings": ["The campus GIS has no published positional accuracy and is not a certified survey."],
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "score": 1.5,
            "max_score": 2.0,
            "evidence": [
                "Structural wall base reproduces the GIS campus coordinates and the object transform is identity.",
                "The evaluated bounds extend about 3.34 m west of the GIS wall boundary, attributable to the front portico/steps; eaves extend only about 0.22 m.",
            ],
            "findings": [
                "The house illustration is not georeferenced, so its facade bearing toward Russell Street is plausible but not verified.",
                "No measured source independently validates the overall building height or roof envelope.",
            ],
        },
        {
            "criterion": "Evidence-backed height, floors, and roof",
            "score": 1.25,
            "max_score": 2.0,
            "evidence": [
                "The artist illustration supports the broad two-story silhouette, twin front gables, central dormers, and chimney.",
                "Modeled eaves are 7.15 m, gable ridge 11.65 m, chimney top 15.3 m; all are stated as estimates.",
            ],
            "findings": [
                "GIS NUM_LEVELS=1 conflicts with the two exterior stories shown in the illustration, and its field definition is unpublished.",
                "GIS Extrution=12 has no documented units or semantics; no measured elevations were found.",
                "The source is a stylized illustration, not a measured elevation or photograph; roof intersections and exact dimensions remain unverified.",
            ],
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 1.5,
            "max_score": 2.0,
            "evidence": [
                "The model visibly includes red-brick wings, twin gables, centered columned portico and pediment, repeated windows, dormers, and a chimney matching the saved Sigma Kappa house illustration.",
                "A fresh visual comparison of the rendered preview and illustration supports the main facade composition.",
            ],
            "findings": [
                "Window groupings and portico proportions are simplified; the illustration does not establish measured dimensions or bearing.",
            ],
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 2.0 if portable and source_images_present else 1.0,
            "max_score": 2.0,
            "evidence": [
                "The .blend reopens in Blender 5.2.3 LTS with the expected collection and one House_301840869 mesh; no camera or light objects remain.",
                f"The object has identity transform, {PROBE['mesh_vertex_count']} vertices, {PROBE['mesh_face_count']} faces, and no external image dependencies.",
                "Building-specific source snapshots, structured evidence, validation output, preview, and evaluator artifacts are present.",
            ],
            "findings": [],
        },
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    return {
        "score": score,
        "max_score": 10,
        "passed": score >= 8.0,
        "criteria": criteria,
        "evidence": {
            "asset_path": "modular/buildings/massing_house_301840869_1b80ace.blend",
            "probe": PROBE,
            "gis_attributes": {k: attributes.get(k) for k in ["FID", "BUILDING_N", "BLDG_ABBR", "ADDRESS", "Shape__Area", "Shape__Length", "NUM_LEVELS", "Extrution"]},
            "source_observations": OBS["sources"],
            "source_image_snapshots_present": source_images_present,
        },
        "findings": [
            "PASS: latest score reaches the 8/10 threshold." if score >= 8 else "FAIL: score is below the 8/10 threshold.",
            "Building identity, address, campus placement, and wall footprint have strong source support.",
            "Floor count, all vertical dimensions, and exact facade orientation remain uncertain.",
            "The exterior illustration is useful for broad style only; it cannot validate measured dimensions.",
        ],
    }


result = evaluate()
(HERE / "result.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
(HERE / "evaluator_output.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
print(json.dumps(result, indent=2))
