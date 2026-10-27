"""Promote the independently graded Evans Scholars House local asset."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULAR = ROOT / "modular"
ASSET_ID = "massing_house_301841610_b6ad6ed"
ASSET_PATH = MODULAR / "buildings" / f"{ASSET_ID}.blend"
SOURCE_PATH = ROOT / "audit" / "evans_scholars_house" / "source_record.json"
FRESH_PATH = ROOT / "audit" / "evans_scholars_house" / "fresh_open_validation.json"
SUMMARY_PATH = ROOT / "audit" / "evans_scholars_house" / "build_summary.json"
GRADE_PATH = ROOT / "audit" / "evans_scholars_house" / "independent_grade_r1" / "result.json"
OBJECTS_PATH = ROOT / "scratch" / "evans_objects.json"
EXPECTED_SHA = "4f14bbdf897f8416d1b1e67c0d2e8b5041c9c3e7376efcf371e9266260f62cb7"

actual_sha = hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()
if actual_sha != EXPECTED_SHA:
    raise RuntimeError(f"Evans Scholars asset changed since independent review: {actual_sha}")

source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
fresh = json.loads(FRESH_PATH.read_text(encoding="utf-8"))
summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
grade = json.loads(GRADE_PATH.read_text(encoding="utf-8"))
objects = json.loads(OBJECTS_PATH.read_text(encoding="utf-8"))
if grade.get("verdict") != "PASS" or float(grade.get("score", 0)) < 8:
    raise RuntimeError("Evans Scholars independent grade did not meet 8/10")
if grade.get("asset_sha256") != actual_sha or fresh.get("asset_sha256") != actual_sha:
    raise RuntimeError("Evans Scholars sources did not evaluate the current asset hash")
if not fresh.get("fresh_open") or len(objects) != int(fresh.get("objects", -1)):
    raise RuntimeError("Evans Scholars fresh-open/object inventory validation is incomplete")

origin = [float(v) for v in summary["local_centroid_projected_m"]]
local = [[float(fresh["bounds_min_m"][i]), float(fresh["bounds_max_m"][i])] for i in range(3)]
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
    "object_count": int(fresh["objects"]),
    "bounds_world_m": world,
    "exterior_bounds_world_m": world,
    "local_bounds_m": local,
    "accuracy_status": (
        "Independent R1 grade 8.4/10; Purdue GIS FID 755, chapter photos, and the current "
        "1001 Hilltop Dr address support the Evans Scholars house identity and footprint. "
        "Brick, portico, cupola, roof silhouette and entry are imagery-based. Exact height, "
        "roof geometry, hidden elevations, and interior arrangement remain estimates; interior is schematic."
    ),
    "placement_transform": "Placement_<id> collection-instance marker translates local geometry to placement_origin_xy_m",
    "placement_origin_xy_m": origin,
    "local_coordinates": True,
    "independent_grade_score": float(grade["score"]),
    "independent_grade_file": "../audit/evans_scholars_house/independent_grade_r1/result.json",
    "sha256": actual_sha,
    "source_metadata": {
        "purdue_arcgis_fid": 755,
        "building_name": "Evans Scholars House (Purdue Chapter)",
        "address": "1001 Hilltop Dr, West Lafayette, Indiana",
        "evidence_file": "audit/evans_scholars_house/source_record.json",
    },
})
manifest["detailed_asset_count"] = sum(asset.get("kind") == "detailed" for asset in manifest["assets"])
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

source["validation"]["independent_grade"] = {
    "status": "PASS",
    "score": float(grade["score"]),
    "file": "audit/evans_scholars_house/independent_grade_r1/result.json",
}
source["validation"]["master_integration"] = "Integrated through Placement_massing_house_301841610_b6ad6ed; fresh-open validation is in audit/master_integration_evans_scholars_house_2026-10-27.json."
SOURCE_PATH.write_text(json.dumps(source, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print(json.dumps({"asset_id": ASSET_ID, "sha256": actual_sha, "grade": grade["score"], "object_count": len(objects), "placement_origin_xy_m": origin, "bounds_world_m": world}, indent=2))
