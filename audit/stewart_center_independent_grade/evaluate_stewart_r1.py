"""Independent Stewart Center R1 scorecard calculator.

This grades the freshly reopened modular asset against the evidence present in
this audit folder. It intentionally keeps the earlier pre-remediation grade
separate and does not treat it as current authority.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent

criteria = [
    {
        "name": "Identity and GIS footprint fidelity",
        "score": 1.8,
        "max_score": 2.0,
        "evidence": "Purdue GIS layer 0 OBJECTID 615 identifies STEW / Stewart Center. The 52 wall segments follow the cleaned 53-vertex GIS boundary; the reported local wall bounds track transformed GIS bounds to under 0.01 m, and the footprint overlay shows the stepped perimeter.",
        "limitations": "The campus GIS polygon is a mapping footprint, not a measured facade survey. It verifies plan outline only, not wall offsets or architectural articulation.",
    },
    {
        "name": "Placement, orientation, scale, and interior layout",
        "score": 1.4,
        "max_score": 2.0,
        "evidence": "Fresh reopen confirms AssetRoot_stewart_center at identity and origin. The manifest records the established origin [91.0499983, -253.375] m. All three retained module bounding boxes fall within the GIS polygon. The 2024 Road School maps support a south/main entrance and Loeb east/northeast of the central library.",
        "limitations": "The Road School plan has neither north arrow nor scale. Ringel appears west/left of central HSSE on the schematic, while its modeled bounds are centered east of HSSE; module coordinates therefore remain approximate. The current master instance marker was not freshly reopened in this asset-only pass.",
    },
    {
        "name": "Floors, height, and roof form",
        "score": 1.0,
        "max_score": 2.0,
        "evidence": "Purdue archival source supports three floors in the central portion. The asset has walls to 16.5 m and total bounds to 22.5 m, with a flat GIS-bounded roof polygon.",
        "limitations": "Wall and overall heights, roof elevation, and rooftop plant forms are explicitly estimates; no dimensioned elevation or roof plan supports them. The broad flat roof and block-like rooftop forms remain visually generic.",
    },
    {
        "name": "Facade, entrances, and distinctive identity",
        "score": 0.9,
        "max_score": 2.0,
        "evidence": "Fresh south/north oblique renders show perimeter-following brick walls, window rhythm, horizontal base courses, a framed south entrance, glazing, and broad steps. These provide a recognizable massing and entrance treatment.",
        "limitations": "The repeated windows and brick facade still read generically. The available Purdue reference shows a more specific stone-framed/columned entry. The incorporated historic library and reconstructed Fowler Hall are not clearly legible as distinct volumes; the documented mural is not modeled. Roof/context forms also lack clear source support.",
    },
    {
        "name": "Modular integrity, portability, and evidence quality",
        "score": 1.8,
        "max_score": 2.0,
        "evidence": "Blender freshly reopened the exact asset SHA and found 1,940 objects (1,927 meshes), an identity root, zero materialless meshes, and zero missing image dependencies. Build/validation records, GIS snapshot, footprint overlay, floor-map snapshots, and three views are present.",
        "limitations": "Evidence remains weaker for facade dimensions, exact interior offsets, roof, and heights; the master link was not inspected in this independent asset grade.",
    },
]

result = {
    "grade_id": "stewart_center_independent_grade_r1",
    "asset": "modular/buildings/stewart_center.blend",
    "asset_sha256": "a3d7e9aba5cf2d32aa0aef5d458dfb6225841126c6a43c272bb60011fe310249",
    "fresh_reopen_object_count": 1940,
    "fresh_reopen_mesh_count": 1927,
    "score": round(sum(c["score"] for c in criteria), 1),
    "max_score": 10.0,
    "pass_threshold": 8.0,
    "passed": sum(c["score"] for c in criteria) >= 8.0,
    "criteria": criteria,
    "evidence_files": [
        "building_validation.json",
        "independent_reopen_r1.json",
        "structural_wall_probe.json",
        "purdue_gis_feature_615.json",
        "footprint_overlay.png",
        "roadschool_maps_2024.pdf",
        "roadschool_floor-1.png",
        "roadschool_floor-2.png",
        "roadschool_floor-3.png",
        "south_oblique.png",
        "north_oblique.png",
        "top.png",
        "BUILD_RECORD.md",
    ],
}

(ROOT / "independent_grade_r1.json").write_text(
    json.dumps(result, indent=2) + "\n", encoding="utf-8"
)

if __name__ == "__main__":
    print(json.dumps({"score": result["score"], "passed": result["passed"]}, indent=2))
