"""Promote the Delta Delta Delta source library to a detailed master asset."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULAR = ROOT / "modular"
ASSET_ID = "massing_house_301841333_affe21e"
ASSET_PATH = MODULAR / "buildings" / f"{ASSET_ID}.blend"
EVIDENCE_PATH = ROOT / "audit" / "delta_delta_delta" / "evidence.json"
FRESH_PATH = ROOT / "audit" / "delta_delta_delta" / "fresh_open_validation.json"
GRADE_PATH = ROOT / "audit" / "delta_delta_delta" / "independent_grade_r1" / "result.json"

EXPECTED_SHA = "0890efdbbb2eff92dfbfd6a60d69a6d4006108a029e8d209ef7791b34182b376"
actual_sha = hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()
if actual_sha != EXPECTED_SHA:
    raise RuntimeError(f"Frozen Delta Delta Delta asset changed: {actual_sha}")

evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
fresh = json.loads(FRESH_PATH.read_text(encoding="utf-8"))
grade = json.loads(GRADE_PATH.read_text(encoding="utf-8"))
if not fresh.get("scene") or fresh.get("collection") is None:
    raise RuntimeError("Fresh-open asset validation is incomplete")
if grade.get("score", 0) < 8 or not grade.get("pass"):
    raise RuntimeError("Independent Delta Delta Delta grade did not pass 8/10")

manifest_path = MODULAR / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
records = [asset for asset in manifest["assets"] if asset["id"] == ASSET_ID]
if len(records) != 1:
    raise RuntimeError(f"Expected one manifest row for {ASSET_ID}; got {len(records)}")
record = records[0]
bound_corners = fresh["evaluated_local_bounds_m"]
local = [[float(bound_corners[0][i]), float(bound_corners[1][i])] for i in range(3)]
origin = evidence["placement"]["origin_xy_m"]
world = [[float(local[i][j]) + (float(origin[i]) if i < 2 else 0.0)
          for j in range(2)] for i in range(3)]

record.update({
    "kind": "detailed",
    "object_count": int(fresh["collection_object_count"]),
    "bounds_world_m": world,
    "exterior_bounds_world_m": world,
    "local_bounds_m": local,
    "accuracy_status": (
        "Independent R1 grade 8.3/10; current Delta Delta Delta Gamma Iota identity is "
        "supported by Purdue FSCL and current map results at the GIS FID 753 address. "
        "Two-story buff masonry facade, rounded portico, arched lower windows and dark "
        "low-pitch roof are imagery-based. The 1200 vs. 898 Tower Dr label mismatch, GIS "
        "NUM_LEVELS=1 conflict, exact height/roof and schematic interior remain unresolved."
    ),
    "placement_transform": "Placement_<id> collection-instance marker translates local geometry to placement_origin_xy_m",
    "placement_origin_xy_m": origin,
    "local_coordinates": True,
    "independent_grade_score": float(grade["score"]),
    "independent_grade_file": "../audit/delta_delta_delta/independent_grade_r1/result.json",
    "sha256": actual_sha,
    "source_metadata": {
        "purdue_arcgis_fid": 753,
        "building_name": "Delta Delta Delta / Gamma Iota chapter house",
        "address": "1200 Tower Dr, West Lafayette, Indiana (GIS/map place address)",
        "evidence_file": "audit/delta_delta_delta/evidence.json",
        "panorama_address_conflict": "Panorama viewpoint card says 898 Tower Dr; parcel/address crosswalk remains uncertain.",
    },
})
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
evidence["independent_grade"] = {
    "status": "PASS",
    "score": float(grade["score"]),
    "file": "audit/delta_delta_delta/independent_grade_r1/result.json",
}
evidence["placement"]["master_integration_required"] = (
    "Integrated via Placement_massing_house_301841333_affe21e; fresh-open master verification "
    "is recorded in audit/master_integration_pi_beta_phi_delta_delta_delta_2026-10-27.json."
)
EVIDENCE_PATH.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"asset_id": ASSET_ID, "sha256": actual_sha, "grade": grade["score"], "world_bounds_m": world}, indent=2))
