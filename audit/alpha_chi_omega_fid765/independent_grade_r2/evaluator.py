"""Independent Alpha Chi Omega R2 grade record for the exact asset revision."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / "modular/buildings/alpha_chi_omega_fid765.blend"
BASE = ROOT / "audit/alpha_chi_omega_fid765"
EXPECTED_SHA256 = "6b78e8672babcdabe630369fdd6d441ce5b9b7e061378a21186881e241763be3"


def evaluate() -> dict:
    actual = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    if actual != EXPECTED_SHA256:
        raise RuntimeError(f"Asset revision changed: expected {EXPECTED_SHA256}, got {actual}")
    build = json.loads((BASE / "build_result.json").read_text(encoding="utf-8"))
    fresh = json.loads((BASE / "fresh_open_validation.json").read_text(encoding="utf-8"))
    crosswalk = json.loads((BASE / "gis_crosswalk.json").read_text(encoding="utf-8"))
    assert build["build_sha256"] == fresh["asset_sha256"] == actual
    assert build["source_feature"]["fid"] == crosswalk["source_feature"]["FID"] == 765
    assert fresh["fresh_open"] and fresh["export_collection"] == "Asset_alpha_chi_omega_fid765"
    assert not fresh["external_file_images"]
    assert not fresh["external_image_texture_nodes"]
    assert not fresh["linked_blend_libraries"]
    result = json.loads((Path(__file__).with_name("result.json")).read_text(encoding="utf-8"))
    assert result["evaluated_sha256"] == actual
    assert abs(sum(item["score"] for item in result["criteria"]) - result["score"]) < 1e-9
    return result


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
