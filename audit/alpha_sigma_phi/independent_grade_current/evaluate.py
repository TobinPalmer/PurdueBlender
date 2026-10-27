"""Independent Alpha Sigma Phi review; run with the project host Python."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
GRADE_DIR = Path(__file__).resolve().parent
ASSET = ROOT / "modular/buildings/massing_house_301841603_654031c.blend"
EVIDENCE = ROOT / "audit/alpha_sigma_phi/source_provenance.json"
FRESH = GRADE_DIR / "fresh_probe.json"


def evaluate():
    probe = json.loads(FRESH.read_text(encoding="utf-8"))
    provenance = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    digest = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    fresh = probe["asset_sha256"] == digest and probe["collection_found"] and probe["scene_found"]
    footprint = probe["source_to_model_footprint"]
    return {
        "building": "Alpha Sigma Phi (Alpha Pi chapter), Purdue",
        "asset": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
        "asset_sha256": digest,
        "grader": "Independent review; candidate fresh-opened and inspected separately from builder",
        "score": 8.2 if fresh and footprint["symmetric_vertex_nearest_max_m"] < 0.001 else 0.0,
        "max_score": 10,
        "pass": bool(fresh and footprint["symmetric_vertex_nearest_max_m"] < 0.001 and probe["materialless_meshes"] == [] and probe["external_images"] == []),
        "criteria": [
            {
                "criterion": "Correct identity and source-backed footprint",
                "score": 1.9,
                "max_score": 2,
                "evidence": [
                    "Purdue ArcGIS FID 763 names Alpha Sigma Phi, gives 951 David Ross Road, and supplies the eight-vertex footprint.",
                    "The chapter history and current chapter source independently corroborate the 951 David Ross Road address.",
                    f"Fresh Blender inspection found {footprint['source_unique_xy_vertices']} GIS and {footprint['model_base_unique_xy_vertices']} modeled base vertices; symmetric nearest-vertex maximum error is {footprint['symmetric_vertex_nearest_max_m']:.6f} m.",
                    "The saved aerial overlay visually shows the GIS polygon tracking the L-shaped roof.",
                ],
                "deduction": "0.1: chapter occupancy and current facade are not independently confirmed by a direct recent target-facing photograph; the identity is strongly supported by official GIS and chapter address sources but not a visual occupancy check.",
            },
            {
                "criterion": "Position, orientation, and scale/dimensions",
                "score": 2.0,
                "max_score": 2,
                "evidence": [
                    "The frozen asset root has identity transform (zero translation/rotation, unit scale), with the footprint vertices already in project campus coordinates.",
                    "Independent source-to-model vertex comparison is within 0.000062 m, confirming source-derived plan geometry and its orientation.",
                    "Fresh-open world bounds are X -1035.7644 to -1004.0955 m, Y 830.2736 to 874.3992 m, Z -0.03 to 10.44 m.",
                    "Aerial imagery shows the same L-shaped roof outline and surrounding lot placement.",
                ],
                "deduction": None,
            },
            {
                "criterion": "Evidence-backed height, floors, and roof form",
                "score": 1.3,
                "max_score": 2,
                "evidence": [
                    "2018 Indiana 3DEP LiDAR target tile was independently documented; median unclassified returns inside the footprint and nearby class-2 ground returns yield a 10.06 m roof-surface proxy.",
                    "The aerial image supports a broad, low-slope/flat L-shaped roof plan and the model reproduces that outline.",
                    "The saved Blender model has an approximately 10.44 m maximum envelope including roof/parapet details.",
                ],
                "deduction": "0.7: the LiDAR proxy is not a surveyed wall height (no class-6 building points, noisy roof surface and weak plane fit); Purdue GIS reports NUM_LEVELS=1/CountOfFLO=1 while the model uses three window levels. The flat roof is supported in plan but no elevation resolves parapet or roof-wall height.",
            },
            {
                "criterion": "Facade, entrances, and distinctive architecture",
                "score": 1.1,
                "max_score": 2,
                "evidence": [
                    "The exterior render shows a consistent masonry running-bond material, repeated framed windows, a recessed main entry/canopy, and a parapet along the L-shaped mass.",
                    "The 1976/1979 Alpha Pi archives support house use, a social room, dining-room finish, hallway, and trophy case; the cutaway includes these as clearly identified schematic spaces.",
                    "A current street-view panorama was reviewed, but trees and neighboring buildings obscure the target and do not establish this facade design.",
                ],
                "deduction": "0.9: target-specific brick tone, three-level window rhythm, exact window spacing, parapet, and entry position are estimates without a usable target-facing elevation; no verified chapter lettering/signage or distinctive exterior detail is represented. Interior room placement is illustrative rather than plan-derived.",
            },
            {
                "criterion": "Modular export, portability, and complete evidence",
                "score": 1.9,
                "max_score": 2,
                "evidence": [
                    "Fresh-opened the exact asset SHA-256 in Blender 5.2.3 LTS; expected scene and asset collection exist.",
                    f"The asset collection contains {probe['collection_object_count']} mesh objects and 12 assigned materials; no materialless meshes or external file-backed images were found.",
                    "Stable asset filename, collection, scene, and root object names are preserved. Review camera/sun are outside the asset collection.",
                    "Evidence folder includes source snapshots, provenance, LiDAR analysis, aerial overlay, exterior/interior preview renders, and fresh-open validation.",
                ],
                "deduction": "0.1: the saved asset file also contains an unrelated default Cube in a separate empty Scene; it is outside the exported asset collection and does not affect collection linking, but makes the file slightly less clean.",
            },
        ],
        "evidence": {
            "fresh_probe": str(FRESH.relative_to(ROOT)).replace("\\", "/"),
            "builder_fresh_validation": "audit/alpha_sigma_phi/fresh_open_validation.json",
            "source_provenance": "audit/alpha_sigma_phi/source_provenance.json",
            "aerial_overlay": "audit/alpha_sigma_phi/sources/esri_world_imagery_fid763_footprint_overlay.png",
            "lidar_analysis": "audit/alpha_sigma_phi/lidar_height_evidence_2018.json",
            "exterior_preview": "audit/alpha_sigma_phi/previews/alpha_sigma_phi_exterior.png",
            "interior_preview": "audit/alpha_sigma_phi/previews/alpha_sigma_phi_interior_cutaway.png",
            "fresh_reopen": fresh,
            "footprint_symmetric_vertex_max_error_m": footprint["symmetric_vertex_nearest_max_m"],
            "asset_hash_matches_frozen_candidate": digest.lower() == "fb713777b45c7e2d9b98e94c4acaf4b5ccdb11a45dc225e88a1af929a2d96d3e",
        },
        "findings": [
            "Passes 8/10 at 8.2/10, with explicit uncertainty deducted for the unsupported floor count and target-specific facade details.",
            "Keep the three-level arrangement labeled as an interpretation: LiDAR supports roof envelope, but the GIS floor-count attributes conflict and do not establish stories.",
            "At master integration, coordinator should update stale manifest metadata (currently massing/object_count 1/bounds Z max 7.6 m) to reflect this 870-object detailed asset and actual dimensions; grader did not edit shared files.",
            "If later photographic evidence becomes available, verify the front entry, facade/window rhythm, and chapter signage before increasing the architectural-detail score.",
        ],
    }


if __name__ == "__main__":
    report = evaluate()
    (GRADE_DIR / "result.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary = f"Alpha Sigma Phi: {report['score']:.1f}/10 ({'PASS' if report['pass'] else 'FAIL'})"
    (GRADE_DIR / "result.md").write_text(summary + "\n\n" + "\n".join(f"- {c['criterion']}: {c['score']:.1f}/2" for c in report["criteria"]) + "\n\n" + "\n".join(f"- {x}" for x in report["findings"]) + "\n", encoding="utf-8")
    print(summary)
