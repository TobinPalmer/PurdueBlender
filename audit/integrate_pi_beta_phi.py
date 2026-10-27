"""Promote the Pi Beta Phi source library to a detailed master asset."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULAR = ROOT / "modular"
ASSET_ID = "massing_house_301838781_891384f"
ASSET_PATH = MODULAR / "buildings" / f"{ASSET_ID}.blend"
EVIDENCE_PATH = ROOT / "audit" / "pi_beta_phi" / "evidence.json"
FRESH_PATH = ROOT / "audit" / "pi_beta_phi" / "fresh_open_validation.json"
GRADE_PATH = ROOT / "audit" / "pi_beta_phi" / "independent_grade_r1" / "result.json"

EXPECTED_SHA = "8c1684ed6e4486fe2200af68600821c6c1f739db8939dd495ac5bdfe5b8e58c7"
ORIGIN = [-429.57778493112545, -311.88038117902056]

actual_sha = hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()
if actual_sha != EXPECTED_SHA:
    raise RuntimeError(f"Frozen Pi Beta Phi asset changed: {actual_sha}")

evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
fresh = json.loads(FRESH_PATH.read_text(encoding="utf-8"))
grade = json.loads(GRADE_PATH.read_text(encoding="utf-8"))
if not fresh.get("scene_name_ok") or not fresh.get("collection_present"):
    raise RuntimeError("Fresh-open asset validation did not pass")
if grade.get("score", 0) < 8 or not grade.get("pass"):
    raise RuntimeError("Independent Pi Beta Phi grade did not pass 8/10")

local = evidence["asset"]["local_bounds_xyz_m"]
world = [[float(local[i][j]) + (ORIGIN[i] if i < 2 else 0.0)
          for j in range(2)] for i in range(3)]
manifest_path = MODULAR / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
records = [asset for asset in manifest["assets"] if asset["id"] == ASSET_ID]
if len(records) != 1:
    raise RuntimeError(f"Expected one manifest row for {ASSET_ID}; got {len(records)}")
record = records[0]

record.update({
    "kind": "detailed",
    "object_count": int(fresh["object_count"]),
    "bounds_world_m": world,
    "exterior_bounds_world_m": world,
    "local_bounds_m": local,
    "accuracy_status": (
        "Independent R1 grade 8.5/10; current Pi Beta Phi Indiana Delta main house, "
        "Purdue GIS FID 774 at 1012 State St. The modeled structural shell matches the "
        "GIS polygon (IoU 0.99999998; Hausdorff 0.000000903 m). Exact story heights, "
        "roof/parapet construction, floor plan, and interior arrangement remain estimated; "
        "separate FID 841 is excluded pending identity resolution."
    ),
    "placement_transform": "Placement_<id> collection-instance marker translates local geometry to placement_origin_xy_m",
    "placement_origin_xy_m": ORIGIN,
    "local_coordinates": True,
    "independent_grade_score": float(grade["score"]),
    "independent_grade_file": "../audit/pi_beta_phi/independent_grade_r1/result.json",
    "sha256": actual_sha,
    "source_metadata": {
        "purdue_arcgis_fid": 774,
        "building_name": "Pi Beta Phi / Indiana Delta chapter house",
        "address": "1012 State Street, West Lafayette, Indiana",
        "evidence_file": "audit/pi_beta_phi/evidence.json",
        "separate_fid_841_excluded": True,
    },
})
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
evidence["independent_grade"] = {
    "status": "PASS",
    "score": float(grade["score"]),
    "file": "audit/pi_beta_phi/independent_grade_r1/result.json",
}
evidence["integration_note"] = (
    "Detailed local-coordinate library integrated into purdue_campus_master.blend via "
    "Placement_massing_house_301838781_891384f; fresh-open master verification is recorded "
    "in audit/master_integration_pi_beta_phi_2026-10-27.json."
)
EVIDENCE_PATH.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"asset_id": ASSET_ID, "sha256": actual_sha, "grade": grade["score"], "world_bounds_m": world}, indent=2))
