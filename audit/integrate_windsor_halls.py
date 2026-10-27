"""Promote the independently graded Windsor Halls R4 asset to a detailed model."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULAR = ROOT / "modular"
ASSET_ID = "massing_windsor_halls_80aeb51"
ASSET_PATH = MODULAR / "buildings" / f"{ASSET_ID}.blend"
BUILD_PATH = ROOT / "audit" / "windsor_halls" / "build_report.json"
FRESH_PATH = ROOT / "audit" / "windsor_halls" / "fresh_open_raw.json"
VALIDATION_PATH = ROOT / "audit" / "windsor_halls" / "validation.json"
GRADE_PATH = ROOT / "audit" / "windsor_halls" / "independent_grade_r4" / "result.json"
OBJECTS_PATH = ROOT / "scratch" / "windsor_objects.json"
EXPECTED_SHA = "c6dd5a4fa121afa0619e545de29717ab759396396654c16075ebbd7899bdd1a9"

actual_sha = hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()
if actual_sha != EXPECTED_SHA:
    raise RuntimeError(f"Windsor Halls asset changed since independent review: {actual_sha}")

build = json.loads(BUILD_PATH.read_text(encoding="utf-8"))
fresh = json.loads(FRESH_PATH.read_text(encoding="utf-8"))
validation = json.loads(VALIDATION_PATH.read_text(encoding="utf-8"))
grade = json.loads(GRADE_PATH.read_text(encoding="utf-8"))
objects = json.loads(OBJECTS_PATH.read_text(encoding="utf-8"))
if not grade.get("passed") or float(grade.get("score", 0)) < 8:
    raise RuntimeError("Windsor Halls independent grade did not meet 8/10")
if grade.get("asset_sha256") != actual_sha:
    raise RuntimeError("Windsor Halls grader did not evaluate the current asset")
if not fresh.get("fresh_open") or not validation.get("fresh_open", {}).get("fresh_open"):
    raise RuntimeError("Windsor Halls fresh-open validation is incomplete")
if len(objects) != int(fresh.get("collection_object_count", -1)):
    raise RuntimeError("Windsor Halls object name count does not match the fresh-open result")

origin = [float(v) for v in build["placement_origin_campus_xy_m"]]
bounds = fresh["bounds_m"]
local = [[float(bounds[kmin]), float(bounds[kmax])]
         for kmin, kmax in (("xmin", "xmax"), ("ymin", "ymax"), ("zmin", "zmax"))]
world = [[local[i][j] + (origin[i] if i < 2 else 0.0) for j in range(2)] for i in range(3)]

manifest_path = MODULAR / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
records = [asset for asset in manifest["assets"] if asset["id"] == ASSET_ID]
if len(records) != 1:
    raise RuntimeError(f"Expected one manifest row for {ASSET_ID}; found {len(records)}")
record = records[0]
record.update({
    "kind": "detailed",
    "objects": objects,
    "object_count": int(fresh["collection_object_count"]),
    "bounds_world_m": world,
    "exterior_bounds_world_m": world,
    "local_bounds_m": local,
    "accuracy_status": (
        "Independent R4 grade 8.1/10; four separate Windsor components (Warren, Wood, "
        "Vawter, and Dining Court) match Purdue GIS FIDs 63-66 with footprint IoU "
        "0.999999845-0.999999950. Roof relief and facades are source-informed visual "
        "estimates; interiors are schematic, and vertical elevations/roof heights remain unverified."
    ),
    "placement_transform": "Placement_<id> collection-instance marker translates local geometry to placement_origin_xy_m",
    "placement_origin_xy_m": origin,
    "local_coordinates": True,
    "independent_grade_score": float(grade["score"]),
    "independent_grade_file": "../audit/windsor_halls/independent_grade_r4/result.json",
    "sha256": actual_sha,
    "source_metadata": {
        "purdue_arcgis_fids": [63, 64, 65, 66],
        "building_name": "Windsor Halls: Warren, Wood, Vawter, and Windsor Dining Court",
        "address": "203, 205, and 211 N Russell St, West Lafayette, Indiana",
        "evidence_file": "audit/windsor_halls/build_report.json",
        "excluded_adjacent_fids": [277, 278],
    },
})
manifest["detailed_asset_count"] = sum(asset.get("kind") == "detailed" for asset in manifest["assets"])
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

evidence_path = ROOT / "audit" / "windsor_halls" / "evidence.json"
evidence = {
    "asset_id": ASSET_ID,
    "asset_sha256": actual_sha,
    "independent_grade": {"status": "PASS", "score": float(grade["score"]), "file": "independent_grade_r4/result.json"},
    "placement_origin_xy_m": origin,
    "included_fids": build["included_fids"],
    "excluded_fids": [277, 278],
    "integration": "Integrated as a single linked detailed collection through Placement_massing_windsor_halls_80aeb51; master fresh-open validation is in audit/master_integration_windsor_halls_2026-10-27.json.",
    "known_uncertainty": ["Roof height and profiles remain estimated.", "Hall-specific facade details are based on imagery, not measured elevations.", "Interiors are schematic and not as-built plans."],
}
evidence_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"asset_id": ASSET_ID, "sha256": actual_sha, "grade": grade["score"], "object_count": len(objects), "placement_origin_xy_m": origin, "bounds_world_m": world}, indent=2))
