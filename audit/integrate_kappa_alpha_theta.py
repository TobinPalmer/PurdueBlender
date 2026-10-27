"""Promote the independently graded Kappa Alpha Theta asset to the master manifest."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULAR = ROOT / "modular"
ASSET_ID = "massing_house_301840865_cbf7de2"
ASSET_PATH = MODULAR / "buildings" / f"{ASSET_ID}.blend"
EVIDENCE_PATH = ROOT / "audit" / "kappa_alpha_theta" / "evidence.md"
FRESH_PATH = ROOT / "audit" / "kappa_alpha_theta" / "independent_grade_r1" / "fresh_open_probe.json"
GRADE_PATH = ROOT / "audit" / "kappa_alpha_theta" / "independent_grade_r1" / "result.json"
EXPECTED_SHA = "20dc22e31a3fa189e258b1d22084cbbc646dbdfdc4b643c30a9510f61652bdcd"
ORIGIN = [-496.8858331765, 343.5669554848]

actual_sha = hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()
if actual_sha != EXPECTED_SHA:
    raise RuntimeError(f"Kappa Alpha Theta asset changed after grading: {actual_sha}")
fresh = json.loads(FRESH_PATH.read_text(encoding="utf-8"))
grade = json.loads(GRADE_PATH.read_text(encoding="utf-8"))
if grade.get("actual_sha256") != actual_sha or not grade.get("pass") or float(grade.get("score_out_of_10", 0)) < 8:
    raise RuntimeError("Kappa Alpha Theta independent grade does not pass on the current asset")
if fresh.get("sha256") != actual_sha or fresh.get("asset_id") != ASSET_ID:
    raise RuntimeError("Kappa Alpha Theta fresh-open probe does not describe the current asset")
objects = [obj["name"] for obj in fresh["objects"]]
if len(objects) != int(fresh["object_count"]):
    raise RuntimeError("Kappa Alpha Theta object inventory count mismatch")

local = [[float(bounds[0]), float(bounds[1])] for bounds in fresh["bounds_local_m"]]
world = [[local[i][j] + (ORIGIN[i] if i < 2 else 0.0) for j in range(2)] for i in range(3)]
manifest_path = MODULAR / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
rows = [asset for asset in manifest["assets"] if asset["id"] == ASSET_ID]
if len(rows) != 1:
    raise RuntimeError(f"Expected exactly one manifest row for {ASSET_ID}; found {len(rows)}")
record = rows[0]
record.update({
    "kind": "detailed",
    "objects": objects,
    "object_count": int(fresh["object_count"]),
    "bounds_world_m": world,
    "exterior_bounds_world_m": world,
    "local_bounds_m": local,
    "accuracy_status": (
        "Independent R1 grade 8.2/10. Official Purdue FID 786 and Alpha Chi sources support "
        "Kappa Alpha Theta at 607 N Russell St; its transformed GIS envelope and centroid "
        "anchor are used for approximate placement. The court, brick wings, entry and materials "
        "are photo-informed. The building wall line does not have surveyed elevation control; "
        "story/roof dimensions, facade bearing and hidden elevations remain estimated. Interior "
        "is explicitly schematic. Independent grader notes the entry gable and pale stone lintels "
        "could be closer to photos."
    ),
    "placement_transform": "Placement_<id> collection-instance marker translates local geometry to placement_origin_xy_m",
    "placement_origin_xy_m": ORIGIN,
    "local_coordinates": True,
    "independent_grade_score": float(grade["score_out_of_10"]),
    "independent_grade_file": "../audit/kappa_alpha_theta/independent_grade_r1/result.json",
    "sha256": actual_sha,
    "source_metadata": {
        "purdue_arcgis_fid": 786,
        "building_name": "Kappa Alpha Theta / Alpha Chi chapter house",
        "address": "607 N Russell St, West Lafayette, Indiana",
        "evidence_file": "audit/kappa_alpha_theta/evidence.md",
    },
})
manifest["detailed_asset_count"] = sum(asset.get("kind") == "detailed" for asset in manifest["assets"])
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

integration = {
    "asset_id": ASSET_ID,
    "sha256": actual_sha,
    "grade": float(grade["score_out_of_10"]),
    "grade_result": "audit/kappa_alpha_theta/independent_grade_r1/result.json",
    "placement_origin_xy_m": ORIGIN,
    "local_bounds_m": local,
    "expected_bounds_world_m": world,
    "object_count": int(fresh["object_count"]),
    "integration": "Detailed local-coordinate library; master rebuild and fresh-open marker validation pending.",
}
(ROOT / "audit" / "kappa_alpha_theta" / "integration.json").write_text(json.dumps(integration, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(integration, indent=2, ensure_ascii=False))
