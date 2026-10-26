"""Recalculate the independent R4 score total and validate linked evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "audit" / "tarkington_hall"
grade = json.loads((OUT / "independent_grade_r4.json").read_text(encoding="utf-8"))
expected = "b844a77e35ad44bf722ea0432ed40dc47a6b01fff24c095cbabf68e760f87065"
asset = OUT / "tarkington_hall_r4_candidate.blend"
reopen = json.loads((OUT / "independent_grade_r4_reopen.json").read_text(encoding="utf-8"))
footprint = json.loads((OUT / "independent_grade_r4_footprint.json").read_text(encoding="utf-8"))
actual = hashlib.sha256(asset.read_bytes()).hexdigest()
criteria = grade["criteria"]
total = sum(float(item["score"]) for item in criteria)
checks = {
    "candidate_hash": actual == expected == grade["sha256"] == reopen["sha256"] == footprint["candidate_sha256"],
    "fresh_reopen": reopen["collection"] == "Asset_tarkington_hall" and reopen["collection_object_count"] == 1361,
    "connectors_in_export": reopen["connector_objects_in_export"] == 329 and not reopen["connector_objects_outside_export"],
    "connectors_parented": not reopen["connector_parent_errors"],
    "materials_and_mesh_integrity": not reopen["materialless_meshes"] and not reopen["invalid_material_indices"] and not reopen["nonfinite_meshes"],
    "portable_dependencies": not reopen["missing_external_images"] and not reopen["linked_libraries"],
    "footprint_matches_grade": abs(float(footprint["polygon_iou"]) - 0.9524670589928977) < 1e-9,
    "grade_total": abs(total - 8.0) < 1e-9,
    "passes": total >= float(grade["pass_threshold"]),
}
if not all(checks.values()):
    raise SystemExit(json.dumps({"checks": checks, "score_total": total}, indent=2))
print(json.dumps({"score": total, "passed": True, "checks": checks}, indent=2))
