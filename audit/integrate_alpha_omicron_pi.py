"""Promote Alpha Omicron Pi's graded local asset into the campus manifest."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULAR = ROOT / "modular"
ASSET_ID = "massing_house_970455277_a3fb72a"
ASSET_PATH = MODULAR / "buildings" / f"{ASSET_ID}.blend"
SOURCE_PATH = ROOT / "audit" / "alpha_omicron_pi" / "source_register.json"
FRESH_PATH = ROOT / "audit" / "alpha_omicron_pi" / "fresh_open_validation.json"
GRADE_PATH = ROOT / "audit" / "alpha_omicron_pi" / "independent_grade_r2" / "result.json"
OBJECTS_PATH = ROOT / "scratch" / "aoii_objects.json"
EXPECTED_SHA = "3ac83c2841058b6de3a7f19c587e151df6b3751589a82f03ec4f1c6460da5ec7"

actual_sha = hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()
if actual_sha != EXPECTED_SHA:
    raise RuntimeError(f"AOII asset changed since independent review: {actual_sha}")

source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
fresh = json.loads(FRESH_PATH.read_text(encoding="utf-8"))
grade = json.loads(GRADE_PATH.read_text(encoding="utf-8"))
objects = json.loads(OBJECTS_PATH.read_text(encoding="utf-8"))
if grade.get("verdict") != "PASS" or float(grade.get("score", 0)) < 8:
    raise RuntimeError("AOII independent grade did not meet the 8/10 gate")
if grade.get("asset_sha256_actual") != actual_sha:
    raise RuntimeError("AOII grader did not evaluate the current source asset")
if not fresh.get("saved") or fresh.get("scene") != source["model"]["scene"]:
    raise RuntimeError("AOII fresh-open asset validation is incomplete")
if len(objects) != int(fresh["object_count"]):
    raise RuntimeError("AOII object name inventory does not match fresh-open count")

model = source["model"]
origin = [float(value) for value in model["placement_origin_world_xy_m"]]
local = [[float(pair[0]), float(pair[1])] for pair in model["detailed_local_bounds_including_site_furniture_m"].values()]
world = [[local[i][j] + (origin[i] if i < 2 else 0.0) for j in range(2)] for i in range(3)]

manifest_path = MODULAR / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
records = [asset for asset in manifest["assets"] if asset["id"] == ASSET_ID]
if len(records) != 1:
    raise RuntimeError(f"Expected one manifest record for {ASSET_ID}, found {len(records)}")
record = records[0]
record.update({
    "kind": "detailed",
    "objects": objects,
    "object_count": int(fresh["object_count"]),
    "bounds_world_m": world,
    "exterior_bounds_world_m": world,
    "local_bounds_m": local,
    "accuracy_status": (
        "Independent R2 grade 8.4/10. Current AOII Phi Upsilon identity at 242 S Grant is "
        "supported by chapter sources, the 2015 site-plan report, and March 2026 Street View. "
        "Street-facing brick base, beige lap siding, dark shutters, and low hip roof are "
        "visually supported. Exact as-built heights, roof pitch/ridges, side/rear facades, "
        "and interior layout remain estimated; interior is illustrative."
    ),
    "placement_transform": "Placement_<id> collection-instance marker translates local geometry to placement_origin_xy_m",
    "placement_origin_xy_m": origin,
    "local_coordinates": True,
    "independent_grade_score": float(grade["score"]),
    "independent_grade_file": "../audit/alpha_omicron_pi/independent_grade_r2/result.json",
    "sha256": actual_sha,
    "source_metadata": {
        "osm_way": 970455277,
        "building_name": "Alpha Omicron Pi / Phi Upsilon chapter house",
        "address": "242 S Grant St, West Lafayette, Indiana",
        "evidence_file": "audit/alpha_omicron_pi/source_register.json",
        "purdue_fid_756_identity_conflict": "FID 756 is associated with current Phi Sigma Rho at 1001 David Ross; it is not this AOII house.",
    },
})
manifest["detailed_asset_count"] = sum(asset.get("kind") == "detailed" for asset in manifest["assets"])
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

source["model"]["asset_sha256"] = actual_sha
SOURCE_PATH.write_text(json.dumps(source, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"asset_id": ASSET_ID, "sha256": actual_sha, "grade": grade["score"], "object_count": len(objects), "placement_origin_xy_m": origin, "bounds_world_m": world}, indent=2))
