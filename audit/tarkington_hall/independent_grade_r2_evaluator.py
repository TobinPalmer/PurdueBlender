"""Independent R2 scorecard generator for Tarkington Hall."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = Path(__file__).resolve().parent
ASSET = ROOT / "modular/buildings/tarkington_hall.blend"
EXPECTED_SHA = "75aad771c9da9e454bbea76ef48852519fa58997747547f9120977e81a6aede5"
THRESHOLD = 8.0


def read_json(name: str):
    return json.loads((AUDIT / name).read_text(encoding="utf-8"))


def evaluate() -> dict:
    reopen = read_json("independent_reopen_r2.json")
    membership = read_json("independent_membership_r2.json")
    full_scene_footprint = read_json("footprint_comparison_r2.json")
    footprint = read_json("footprint_export_only_r2.json")
    master_audit = json.loads((ROOT / "audit/master_building_audit.json").read_text(encoding="utf-8"))
    master_record = next(row for row in master_audit["records"] if row["id"] == "tarkington_hall")
    actual_sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    assert actual_sha == EXPECTED_SHA == reopen["sha256"]
    assert reopen["fresh_process_reopen"] and reopen["root_transform_identity"]
    assert footprint["feature_id"] == 662 and footprint["building_code"] == "TARK"
    outside_count = len(membership["connector_objects_outside_export"])
    assert outside_count == 96

    criteria = [
        {
            "name": "Identity and source-backed footprint",
            "score": 1.4,
            "max_score": 2.0,
            "evidence": (
                "The saved GIS feature is Purdue FID 662/code TARK, matching Newton Booth Tarkington Residence Hall. "
                "The 2023 Indiana orthophoto is georeferenced and overlaid. For the actual named export collection, "
                f"the structural-shell union has IoU {footprint['export_shell_iou']:.3f}; mean boundary residual is "
                f"{footprint['mean_symmetric_boundary_residual_m']:.2f} m. P95 is "
                f"{footprint['p95_symmetric_boundary_residual_m']:.2f} m and Hausdorff distance is "
                f"{footprint['symmetric_boundary_hausdorff_m']:.2f} m. The full scene, including unexported connector "
                f"objects, yields IoU {full_scene_footprint['polygon_iou']:.3f}; that is not the delivered export. "
                "The GIS outline is explicitly not a surveyed "
                "wall outline and the orthophoto comparison is a roof-edge proxy."
            ),
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 1.0,
            "max_score": 2.0,
            "evidence": (
                f"The model-shell centroid differs from the transformed GIS centroid by "
                f"{footprint['centroid_delta_m'][0]:.2f} m east-west and "
                f"{footprint['centroid_delta_m'][1]:.2f} m north-south (about "
                f"{math.hypot(*footprint['centroid_delta_m']):.2f} m total); axis bounds are broadly similar. "
                f"The older exhaustive master audit still records position error and orientation error as unverified "
                f"({master_record['position_error_m']}, {master_record['orientation_error_degrees']}); its AABB "
                "screening is not a placement or orientation measurement. No surveyed wall dimensions are available."
            ),
        },
        {
            "name": "Massing, floors, height, and roof form",
            "score": 1.3,
            "max_score": 2.0,
            "evidence": (
                "The exterior shows the four-arm residential-hall organization, central core, four occupied floors, "
                "flat roof masses, and roof equipment. Purdue's emergency plan supports the four-floor wing program. "
                "The model reaches about 19.1 m, but the sources do not provide a measured elevation; roof heights, "
                "penthouse sizes, and central-core outline remain estimates. The corrected footprint comparison still "
                "shows substantial perimeter residuals."
            ),
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1.4,
            "max_score": 2.0,
            "evidence": (
                "The fresh exterior image shows a readable four-wing brick residence hall with repeated window bays, "
                "light horizontal bands, roof penthouses, and a marked central entrance. The source-backed corrections "
                "move wing windows and roof equipment with the revised shells and add two north connector forms. "
                "However, the mapped connectors' structural shells and most associated window objects are outside the "
                "named export collection, so the delivered module omits part of the represented form."
            ),
        },
        {
            "name": "Modular export, portability, and evidence",
            "score": 0.8,
            "max_score": 2.0,
            "evidence": (
                f"A fresh Blender 5.2.3 process reopened the exact canonical SHA. The identity root is present; "
                f"the named export collection contains {reopen['collection_object_count']} objects/"
                f"{reopen['mesh_count']} meshes in the export collection, with no "
                "materialless meshes, invalid material indices, missing image files, or foreign linked libraries. "
                f"Yet the scene has {membership['scene_object_count']} objects while Asset_tarkington_hall contains "
                f"only {membership['export_collection_object_count']}; {outside_count} newly added connector objects "
                "are linked to Scene Collection instead of Asset_tarkington_hall. They therefore do not travel with "
                "the manifest/master library link. GIS, orthophoto, room, and change evidence is extensive, but the "
                "canonical export membership defect is blocking."
            ),
        },
    ]
    score = round(sum(item["score"] for item in criteria), 2)
    findings = [
        {
            "priority": "blocker",
            "finding": (
                "Move the 96 connector objects currently outside Asset_tarkington_hall into the named export "
                "collection, then reopen the canonical library and master link to verify their presence."
            ),
        },
        {
            "priority": "high",
            "finding": (
                f"Export-only footprint mismatch remains material: IoU {footprint['export_shell_iou']:.3f}, "
                f"mean boundary residual {footprint['mean_symmetric_boundary_residual_m']:.2f} m, P95 "
                f"{footprint['p95_symmetric_boundary_residual_m']:.2f} m, and Hausdorff "
                f"{footprint['symmetric_boundary_hausdorff_m']:.2f} m. Diagnose the central-core contribution against "
                "the orthophoto; retain the GIS roof-versus-wall uncertainty."
            ),
        },
        {
            "priority": "high",
            "finding": (
                "Obtain or document a fresh master-marker position/orientation check; the root master audit continues "
                "to label both values unverified."
            ),
        },
        {
            "priority": "medium",
            "finding": (
                "Add an interior view beyond the single representative dorm room and keep room dimensions labeled as "
                "approximate unless supported by an as-built plan."
            ),
        },
    ]
    evidence = {
        "asset": "modular/buildings/tarkington_hall.blend",
        "sha256": actual_sha,
        "blender_version": reopen["blender_version"],
        "fresh_reopen": reopen,
        "collection_membership": {
            "scene_object_count": membership["scene_object_count"],
            "export_collection_object_count": membership["export_collection_object_count"],
            "connector_objects_outside_export": outside_count,
        },
        "footprint_metrics": footprint,
        "full_scene_candidate_footprint_metrics_including_unexported_geometry": full_scene_footprint,
        "source_records": {
            "gis": "audit/tarkington_hall/gis_feature_662.json (Purdue GIS FID 662, TARK)",
            "orthophoto_overlay": "audit/tarkington_hall/ortho_footprint_overlay_r2.png",
            "official_orthophoto": "audit/tarkington_hall/indiana_2023_ortho_r1.png",
            "housing_and_program_sources": "audit/tarkington_hall/refinement_r2.md",
            "room_view": "audit/tarkington_hall/room_r6.png",
            "exterior_view": "audit/tarkington_hall/exterior_r2.png",
            "master_audit": "audit/master_building_audit.json (position/orientation/height unverified)",
        },
    }
    return {
        "building": "Tarkington Hall",
        "revision": "R2",
        "score": score,
        "max_score": 10.0,
        "pass_threshold": THRESHOLD,
        "passed": score >= THRESHOLD,
        "criteria": criteria,
        "evidence": evidence,
        "findings": findings,
    }


if __name__ == "__main__":
    result = evaluate()
    out = AUDIT / "independent_grade_r2.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
