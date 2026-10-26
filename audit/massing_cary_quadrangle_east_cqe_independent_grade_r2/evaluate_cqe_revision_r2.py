"""Independent CQE revision grade. Run the Blender probe first, then this file with Python."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "audit/massing_cary_quadrangle_east_cqe_230c813"
GRADE = ROOT / "audit/massing_cary_quadrangle_east_cqe_independent_grade_r2"
ASSET = ROOT / "modular/buildings/massing_cary_quadrangle_east_cqe_230c813.blend"
ASSET_ID = "massing_cary_quadrangle_east_cqe_230c813"


def project(lon: float, lat: float) -> tuple[float, float]:
    """Apply the project's documented approximate campus coordinate conversion."""
    return (
        (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
        (lat - 40.4274) * 111040.0,
    )


def polygon_area(ring: list[list[float]]) -> float:
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(ring, ring[1:])) / 2)


def polygon_length(ring: list[list[float]]) -> float:
    return sum(math.dist(a, b) for a, b in zip(ring, ring[1:]))


def point_segment_distance(point: list[float], a: list[float], b: list[float]) -> float:
    dx, dy = b[0] - a[0], b[1] - a[1]
    denom = dx * dx + dy * dy
    t = 0.0 if denom == 0 else max(0.0, min(1.0, ((point[0]-a[0])*dx + (point[1]-a[1])*dy) / denom))
    return math.dist(point, [a[0] + t * dx, a[1] + t * dy])


def point_ring_distance(point: list[float], ring: list[list[float]]) -> float:
    return min(point_segment_distance(point, a, b) for a, b in zip(ring, ring[1:]))


def directed_boundary_distances(source: list[list[float]], target: list[list[float]]) -> list[float]:
    # Sample each source edge at 0.25 m intervals so long edges are represented fairly.
    samples: list[list[float]] = []
    for a, b in zip(source, source[1:]):
        n = max(1, math.ceil(math.dist(a, b) / 0.25))
        samples.extend([[a[0] + (b[0]-a[0])*i/n, a[1] + (b[1]-a[1])*i/n] for i in range(n)])
    return [point_ring_distance(point, target) for point in samples]


def main() -> dict:
    probe = json.loads((GRADE / "blender_probe.json").read_text(encoding="utf-8"))
    geo = json.loads((EVIDENCE / "sources/purdue_building_shapes_fid639_cqe_2026-10-25.geojson").read_text(encoding="utf-8"))
    source_record = json.loads((EVIDENCE / "source_record.json").read_text(encoding="utf-8"))
    build = json.loads((EVIDENCE / "build_report.json").read_text(encoding="utf-8"))
    assert probe["asset_id"] == ASSET_ID and probe["blender_version"].startswith("4.5.15")
    feature = geo["features"][0]
    props = feature["properties"]
    assert props["FID"] == 639 and props["BLDG_ABBR"] == "CQE"
    source = [list(project(lon, lat)) for lon, lat in feature["geometry"]["coordinates"][0]]
    foundation = next(row for row in probe["object_rows"] if row["name"] == "CQE_Stone_Foundation_Shell")
    model = foundation["bottom_outline_xy"]
    if model[0] != model[-1]:
        model = model + [model[0]]
    s_to_m = directed_boundary_distances(source, model)
    m_to_s = directed_boundary_distances(model, source)
    src_bounds = [[min(p[0] for p in source), max(p[0] for p in source)], [min(p[1] for p in source), max(p[1] for p in source)]]
    model_bounds = foundation["bounds_world"][:2]
    objects = probe["object_rows"]
    gables = [row for row in objects if row["name"].startswith("CQE_Cross_Gable_") and row["name"].endswith("_Brick_Gable_End")]
    result = {
        "score": 7.6,
        "max_score": 10,
        "status": "fail",
        "candidate_commit": None,
        "candidate_commit_status": "uncommitted worktree candidate; evaluator run against the current saved .blend",
        "evaluated_local_date": "2026-10-26",
        "asset_path": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
        "criteria": [
            {
                "criterion": "Correct identity and source-backed footprint",
                "score": 2.0,
                "max_score": 2.0,
                "status": "verified",
                "evidence": f"Reopened asset carries stable ID {probe['asset_id']}; the authoritative Purdue BuildingShapes feature is FID {props['FID']}, BLDG_ABBR={props['BLDG_ABBR']}, name={props['BUILDING_N']}. Independent campus-coordinate projection gives GIS footprint area {polygon_area(source):.3f} m² and perimeter {polygon_length(source):.3f} m. The model foundation outline has area {polygon_area(model):.3f} m² and perimeter {polygon_length(model):.3f} m; boundary comparison sampled at 0.25 m intervals gives source-to-model max/mean {max(s_to_m):.3f}/{sum(s_to_m)/len(s_to_m):.3f} m and model-to-source max/mean {max(m_to_s):.3f}/{sum(m_to_s)/len(m_to_s):.3f} m.",
                "limitations": [],
            },
            {
                "criterion": "Position, orientation, and scale/dimensions",
                "score": 1.9,
                "max_score": 2.0,
                "status": "verified_with_coordinate_limitations",
                "evidence": f"Independent Blender reopen reports world extents {probe['bounds_world_m_xyz']} m; the foundation plan bounds are {model_bounds}. The model outline follows the GIS source within the boundary distances above, and the 2023 Indiana orthophoto alignment image supports its campus placement and north-south orientation. All modeled asset objects have identity transforms.",
                "limitations": ["Placement uses the project's approximate lon/lat-to-meter conversion; no surveyed control point or independent geodetic registration is supplied."],
            },
            {
                "criterion": "Evidence-backed height, floors, and roof form",
                "score": 1.1,
                "max_score": 2.0,
                "status": "partially_supported",
                "evidence": f"Purdue Archives corporate-record search-index text identifies three stories plus basement; official GIS records NUM_LEVELS={props.get('NUM_LEVELS')}, CountOfFLO={props.get('CountOfFLO')}, and Extrution={props.get('Extrution')}. The 1928 Archives image metadata and the reviewed image show a Cary exterior with a long gabled roof, repeated projecting gabled bays, and small gable windows. The revised asset now has {len(gables)} gable-end meshes ({len(gables)//2} paired cross-gable features) and three above-grade window rows; these image features are Cary-wide context only.",
                "limitations": ["The archive image does not identify Cary East, and orthophoto does not resolve exact roof form or gable count; applying those forms/counts to this building is architectural inference.", "The GIS five-level fields conflict with the building-specific three-stories-plus-basement account. Extrution=48 has undocumented units; the asset's 15.08 m overall height remains an estimate, not a measured height."],
            },
            {
                "criterion": "Facade, entrances, and distinctive architecture",
                "score": 0.8,
                "max_score": 2.0,
                "status": "weakly_supported_with_period_context",
                "evidence": "Cary East-specific School Designs extract says its renovation retained its original Collegiate Gothic character; the building-specific Archives description supports brick, stone, and reinforced concrete. The generic 1928 Cary image supports the broad period context of projecting gable forms and small gable windows, not this facade's exact organization. The candidate renders three window rows, belt courses, pilasters, gable end panels, and an entrance arch.",
                "limitations": ["No supplied source identifies the candidate's exact entrance, bay rhythm, pilaster locations, facade materials by elevation, gable placement/count, or cross-gable dimensions. The render shows the new gable pieces sitting on the main roof with no corresponding projecting wall bays, unlike the contextual photograph's projecting facade bays; the exact CQE treatment remains unverified."],
            },
            {
                "criterion": "Modular export, portability, and complete evidence",
                "score": 1.8,
                "max_score": 2.0,
                "status": "verified_with_evidence_limitations",
                "evidence": f"Fresh Blender 4.5.15 LTS reopen succeeded on the current candidate. The expected scene/collection/asset ID resolve; there are {probe['mesh_objects']} mesh objects, all with identity transforms; no external object libraries; measured bounds are {probe['bounds_world_m_xyz']}. Dedicated source records and previews are present, including official footprint/orthophoto snapshots, archival metadata, and a Cary East renovation-source extract.",
                "limitations": ["The external archive record details remain represented by source metadata/search-index capture, and no building-specific exterior elevation has been located."],
            },
        ],
        "evidence": {
            "direct_reopen_probe": str((GRADE / "blender_probe.json").relative_to(ROOT)).replace("\\", "/"),
            "independent_blender_run_log": str((GRADE / "blender_run.log").relative_to(ROOT)).replace("\\", "/"),
            "candidate_build_evidence": str((EVIDENCE / "build_evidence.json").relative_to(ROOT)).replace("\\", "/"),
            "candidate_source_record": str((EVIDENCE / "source_record.json").relative_to(ROOT)).replace("\\", "/"),
            "source_snapshots": [
                "audit/massing_cary_quadrangle_east_cqe_230c813/sources/purdue_building_shapes_fid639_cqe_2026-10-25.geojson",
                "audit/massing_cary_quadrangle_east_cqe_230c813/sources/indiana_2023_orthophoto_cqe.jpg",
                "audit/massing_cary_quadrangle_east_cqe_230c813/sources/purdue_archives_cary_photo_165_metadata_2026-10-26.json",
                "audit/massing_cary_quadrangle_east_cqe_230c813/sources/purdue_archives_cary_photo_162_metadata_2026-10-26.json",
                "audit/massing_cary_quadrangle_east_cqe_230c813/sources/schooldesigns_cary_east_project_extract_2026-10-26.json",
            ],
            "reviewed_visual_evidence": [
                "audit/massing_cary_quadrangle_east_cqe_230c813/cqe_detailed_preview.png",
                "audit/massing_cary_quadrangle_east_cqe_230c813/cqe_top_preview.png",
                "audit/massing_cary_quadrangle_east_cqe_230c813/cqe_orthophoto_footprint_overlay.png",
                "https://earchives.lib.purdue.edu/iiif/2/pbuildings:165/full/full/0/default.jpg",
            ],
            "independent_geometry_comparison": {
                "source_fid": props["FID"],
                "source_xy_bounds_m": src_bounds,
                "source_projected_area_m2": polygon_area(source),
                "model_foundation_outline_area_m2": polygon_area(model),
                "source_projected_perimeter_m": polygon_length(source),
                "model_foundation_outline_perimeter_m": polygon_length(model),
                "source_to_model_boundary_max_mean_m": [max(s_to_m), sum(s_to_m)/len(s_to_m)],
                "model_to_source_boundary_max_mean_m": [max(m_to_s), sum(m_to_s)/len(m_to_s)],
                "cross_gable_end_meshes": len(gables),
                "cross_gable_pairs": len(gables)//2,
                "blend_sha256": probe["blend_sha256"],
            },
            "method": "Reviewer-generated evaluator reopened the current uncommitted .blend in Blender 4.5.15, independently projected the raw GIS polygon using the repository coordinate conversion, compared it to the foundation mesh bottom outline using sampled point-to-segment distances, reviewed the current detailed/top previews and orthophoto overlay, and separately viewed the cited Purdue Archives 1928 image. Prior grade values were not used in the calculations or score.",
        },
        "findings": [
            "The replacement keeps the identity and source-aligned plan footprint, which are strongly supported.",
            "Adding cross-gable forms and attic windows is a reasonable period-context interpretation from the 1928 Cary image, but that image is not labeled as Cary East and does not justify the model's exact gable count or placement.",
            "In the current render, gable-end structures sit on the main roof without projecting facade bays, while the period-context photo shows projecting gabled facade bays; that visual difference and the lack of CQE-specific elevation evidence limit the architectural credit.",
            "Three above-grade rows are consistent with the building-specific historic account, but overall height and floor-count convention remain unresolved; 15.08 m is an estimate only.",
            "Final independent score is below the required 8/10 pass threshold. Candidate remains uncommitted and should not be marked complete on this grade.",
        ],
    }
    assert abs(sum(c["score"] for c in result["criteria"]) - result["score"]) < 1e-9
    output = GRADE / "result.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    main()
