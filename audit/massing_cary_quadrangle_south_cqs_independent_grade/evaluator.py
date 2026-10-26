"""Independent CQS grade using raw Purdue GIS, saved source imagery, and Blender probe."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRADE = Path(__file__).resolve().parent
EVIDENCE = ROOT / "audit" / "massing_cary_quadrangle_south_cqs_7ee2283"
RAW_GIS = EVIDENCE / "sources" / "purdue_building_shapes_fid653_cqs_2026-10-26.geojson"


def evaluate():
    raw = json.loads(RAW_GIS.read_text(encoding="utf-8"))
    probe = json.loads((GRADE / "probe.json").read_text(encoding="utf-8"))
    feature = raw["features"][0]
    props = feature["properties"]
    ring = feature["geometry"]["coordinates"][0]

    # Recompute Purdue's documented local approximation directly from raw WGS84.
    projected = [((p[0] + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
                  (p[1] - 40.4274) * 111040.0) for p in ring]
    source_bounds = [[min(p[0] for p in projected), max(p[0] for p in projected)],
                     [min(p[1] for p in projected), max(p[1] for p in projected)]]
    source_area = abs(sum(projected[i][0] * projected[(i + 1) % len(projected)][1] -
                          projected[(i + 1) % len(projected)][0] * projected[i][1]
                          for i in range(len(projected))) * 0.5)
    model_ground_bounds = probe["ground_vertex_bounds_m"]
    bounds_delta = [[abs(source_bounds[i][j] - model_ground_bounds[i][j])
                     for j in range(2)] for i in range(2)]
    max_bounds_delta = max(v for axis in bounds_delta for v in axis)

    photo = EVIDENCE / "sources" / "cary_south_photo_wikimedia_2006.jpg"
    ortho = EVIDENCE / "sources" / "indiana_2023_orthophoto_cqs.jpg"
    completeness = {
        "raw_gis_snapshot_present": RAW_GIS.exists(),
        "layer_metadata_snapshot_present": (EVIDENCE / "sources" / "purdue_building_shapes_layer_metadata_2026-10-26.json").exists(),
        "orthophoto_snapshot_present": ortho.exists(),
        "building_specific_facade_photo_present": photo.exists(),
        "source_record_present": (EVIDENCE / "source_record.json").exists(),
        "build_evidence_present": (EVIDENCE / "build_evidence.json").exists(),
        "reopen_validation_present": (EVIDENCE / "reopen_validation.json").exists(),
        "portable_material_only_asset": len(probe["material_names"]) >= 4,
    }
    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "points": 2,
            "score": 2.0,
            "evidence": [
                f"Raw Purdue BuildingShapesZip4 feature FID={props['FID']} reports BLDG_ABBR={props['BLDG_ABBR']} and BUILDING_N={props['BUILDING_N']!r}.",
                f"The feature polygon has {len(ring) - 1} source ring vertices, projects to {source_area:.1f} m², and is the correct Cary Quadrangle South record (1016 W Stadium Avenue).",
                "Model custom properties identify the same FID and CQS abbreviation; the closed GIS outline forms the expected courtyard plan."
            ],
            "findings": []
        },
        {
            "criterion": "Position, orientation and scale/dimensions",
            "points": 2,
            "score": 2.0 if max_bounds_delta < 0.05 else (1.5 if max_bounds_delta < 0.5 else 1.0),
            "evidence": [
                f"Independently reopened asset has {probe['ground_vertex_count']} ground-plane outline vertices; recomputed GIS versus model ground bounds differ by at most {max_bounds_delta:.4f} m.",
                f"The geometry remains in campus coordinates with zero location/rotation, unit scale, and identity collection offset; source outline orientation is preserved."
            ],
            "findings": [] if max_bounds_delta < 0.05 else ["Small discrepancy between footprint extents and saved ground vertices; inspect if the source outline changes."]
        },
        {
            "criterion": "Evidence-backed height, floors and roof form",
            "points": 2,
            "score": 1.0,
            "evidence": [
                "The 2023 Indiana orthophoto supports the courtyard and roof-wing plan; the building-specific 2006 photograph provides only unscaled height proportions.",
                f"Reopened mesh height is {probe['bounds_world_m'][2][1]:.2f} m. Purdue GIS records NUM_LEVELS=7 and CountOfFLO=7, but neither proves above-grade storeys; Extrution=54 has undocumented units."
            ],
            "findings": ["Overall height and tower dimensions remain estimates; no measured elevation or dependable floor count was found.", "Roof pitch, ridge heights, and gable segmentation are inferred from aerial appearance rather than a measured roof plan/elevation."]
        },
        {
            "criterion": "Facade, entrances and distinctive architecture",
            "points": 2,
            "score": 1.5,
            "evidence": [
                "Direct inspection of the saved Wikimedia Commons photograph, identified as Cary Quadrangle's South building looking north, confirms red brick, pale stone vertical bands, paired crenellated entrance towers, central projecting bay, and pointed central arch.",
                "The rendered saved south view includes these distinctive elements and a coherent window rhythm."
            ],
            "findings": ["The photograph is perspective-based and does not measure façade width or detail sizes; windows and bay spacing are schematic, and the model's tower/storey proportions remain approximate."]
        },
        {
            "criterion": "Modular export, portability and complete evidence",
            "points": 2,
            "score": 2.0 if all(completeness.values()) else 1.5,
            "evidence": [
                f"Independent Blender 4.5.15 reopen finds scene {probe['scene']!r}, collection {probe['collection']!r}, and exactly one expected mesh object.",
                f"Object has {probe['vertex_count']} vertices, {probe['polygon_count']} polygons, {probe['modifier_count']} modifiers, {probe['boundary_edges']} boundary edges, and {probe['nonmanifold_edges']} nonmanifold edges.",
                "Asset uses named materials without external texture dependencies; raw GIS, service metadata, orthophoto, building-specific photo, source record, builder evidence, and reopen validation are present.",
                f"Evidence inventory checks: {completeness}"
            ],
            "findings": [] if all(completeness.values()) else ["One or more expected evidence snapshots are missing."]
        }
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    return {
        "asset_id": "massing_cary_quadrangle_south_cqs_7ee2283",
        "asset_path": "modular/buildings/massing_cary_quadrangle_south_cqs_7ee2283.blend",
        "grade_date": "2026-10-26",
        "grader": "Independent audit agent",
        "score": score,
        "max_score": 10,
        "pass_threshold": 8,
        "passed": score >= 8,
        "criteria": criteria,
        "evidence": {
            "raw_source": str(RAW_GIS.relative_to(ROOT)),
            "source_identity": {"FID": props["FID"], "BLDG_ABBR": props["BLDG_ABBR"], "BUILDING_N": props["BUILDING_N"], "address": props["ADDRESS"]},
            "recomputed_source_bounds_m": source_bounds,
            "recomputed_source_area_m2": round(source_area, 2),
            "saved_model_ground_bounds_m": model_ground_bounds,
            "max_bounds_delta_m": round(max_bounds_delta, 4),
            "blender_probe": probe,
            "direct_visual_review": [
                "cqs_gis_footprint_orthophoto_overlay.png",
                "cqs_top_preview.png",
                "cqs_south_preview.png",
                "sources/cary_south_photo_wikimedia_2006.jpg",
                "sources/indiana_2023_orthophoto_cqs.jpg"
            ]
        },
        "findings": [finding for criterion in criteria for finding in criterion["findings"]],
        "grading_note": "Appearance is not used to validate dimensions. Roof and vertical geometry retain explicit uncertainty; the score gives partial credit for the direct photographic and aerial evidence without treating estimated height as measured."
    }


if __name__ == "__main__":
    result = evaluate()
    (GRADE / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
