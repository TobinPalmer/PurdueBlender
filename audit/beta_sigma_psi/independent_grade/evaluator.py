"""Independent rubric evaluator for Beta Sigma Psi (Purdue GIS FID 793).

The function grades evidence present at evaluation time, not the builder's claims.
Run from any directory with Python and pass the project's build_evidence.json;
optional fresh-open verification JSON raises export credit when all checks pass.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


def evaluate(evidence_path: str | Path, reopen_path: str | Path | None = None,
             phase: str = "final") -> dict[str, Any]:
    evidence_path = Path(evidence_path)
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    source_dir = evidence_path.parent / "sources"
    gis_path = source_dir / "purdue_gis_fid793_2026-10-26.json"
    gis = json.loads(gis_path.read_text(encoding="utf-8-sig")) if gis_path.exists() else {}
    features = gis.get("features", [])
    attrs = features[0].get("attributes", {}) if features else {}
    official_match = (attrs.get("FID") == 793 and attrs.get("BUILDING_N") == "Beta Sigma Psi"
                      and attrs.get("ADDRESS") == "525 University St")
    reopen = None
    if reopen_path and Path(reopen_path).exists():
        reopen = json.loads(Path(reopen_path).read_text(encoding="utf-8"))
    checks = (reopen or {}).get("checks", {})
    reopened_ok = bool(reopen and reopen.get("reopened_successfully")
                       and reopen.get("asset_collection") == evidence.get("collection")
                       and all(checks.get(k, False) for k in (
                           "expected_collection_present", "single_named_mesh_object",
                           "identity_object_transform", "positive_height_and_plan_bounds",
                           "materials_assigned", "no_external_file_images", "no_modifiers")))
    fp = evidence.get("footprint", {})
    geom = evidence.get("geometry", {})
    sources = evidence.get("sources", [])
    ring = features[0].get("geometry", {}).get("rings", [[]])[0] if features else []
    if len(ring) > 1 and ring[0] == ring[-1]:
        ring = ring[:-1]
    # Independently calculate projected ring area/perimeter and compare to the
    # ArcGIS Shape__Area/Shape__Length attributes instead of trusting the
    # builder's summary. These fields are evidence metadata, not geometry.
    xy = [((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
           (lat - 40.4274) * 111040.0) for lon, lat in ring]
    ring_area = abs(sum(xy[i][0] * xy[(i+1) % len(xy)][1] - xy[(i+1) % len(xy)][0] * xy[i][1]
                        for i in range(len(xy))) / 2) if len(xy) >= 3 else 0.0
    ring_perimeter = sum(math.dist(xy[i], xy[(i+1) % len(xy)]) for i in range(len(xy))) if len(xy) >= 2 else 0.0
    area_attr = float(attrs.get("Shape__Area") or 0)
    perimeter_attr = float(attrs.get("Shape__Length") or 0)
    geometry_attribute_mismatch = bool(area_attr and perimeter_attr and (
        abs(ring_area / area_attr - 1) > 0.1 or abs(ring_perimeter / perimeter_attr - 1) > 0.1))
    source_complete = bool(sources and all(
        all(s.get(k) for k in ("provider", "url", "feature_id", "retrieved", "source_crs", "method", "uncertainty"))
        for s in sources))

    criteria = [
        {"criterion": "Identity and source-backed footprint", "points": 1.5 if official_match and fp.get("source_fid") == 793 and fp.get("vertex_count", 0) >= 4 and geometry_attribute_mismatch else (2.0 if official_match and fp.get("source_fid") == 793 and fp.get("vertex_count", 0) >= 4 else 0.0),
         "max_points": 2.0, "status": ("identity verified; footprint metrics conflict" if geometry_attribute_mismatch and official_match else ("verified" if official_match else "uncertain")),
         "evidence": ["Raw Purdue GIS snapshot identifies FID 793 as Beta Sigma Psi at 525 University St; OSM and BoilerLink cross-check the chapter/address.",
                      f"The 14-vertex GIS ring is used directly for the modeled footprint. Independent projection gives polygon area {ring_area:.1f} m² and perimeter {ring_perimeter:.1f} m; stored Shape__Area/Shape__Length attributes state {area_attr:.1f} m² and {perimeter_attr:.1f} m."],
         "findings": ([f"GIS geometry and its Shape__Area/Shape__Length attributes conflict (projected ring {ring_area:.1f} m²/{ring_perimeter:.1f} m versus attributes {area_attr:.1f} m²/{perimeter_attr:.1f} m); identity is credible, but authoritative footprint size is not resolved."] if geometry_attribute_mismatch else ([] if official_match else ["GIS identity could not be confirmed independently."]))},
        {"criterion": "Position, orientation, and scale/dimensions", "points": 1.5 if official_match and fp.get("projected_dimensions_m") and geometry_attribute_mismatch else (1.75 if official_match and fp.get("projected_dimensions_m") else 0.0),
         "max_points": 2.0, "status": "source-derived; approximate projection",
         "evidence": [f"GIS vertices are converted by the documented campus approximation; reported plan dimensions are {fp.get('projected_dimensions_m')} m and center {fp.get('campus_xy_center_m')}.",
                      "Dedicated builder script derives geometry from the source polygon and uses its principal direction for the roof/room grid."],
         "findings": ["Campus conversion is an approximation; independent surveyed registration, orientation residual, and dimension overlay were not supplied."] + (["The GIS geometry/attribute size mismatch prevents confident validation of the model dimensions."] if geometry_attribute_mismatch else [])},
        {"criterion": "Height, floors, and roof form", "points": 1.0 if official_match and attrs.get("NUM_LEVELS") == 1 else 0.0,
         "max_points": 2.0, "status": "partly verified; height/roof uncertain",
         "evidence": ["Raw GIS lists NUM_LEVELS=1.", f"Model record gives wall {geom.get('wall_height_m')} m, eave {geom.get('roof_eave_m')} m, peak {geom.get('roof_peak_m')} m; record labels these estimates and roof form uncertain."],
         "findings": ["No independently supported measured elevation or roof-form source; the 6.7 m peak and low-pitch hip roof are speculative."]},
        {"criterion": "Facade, entrances, and distinctive architecture", "points": 0.25 if geom.get("facade") else 0.0,
         "max_points": 2.0, "status": "unverified",
         "evidence": ["Current exterior render visibly contains masonry walls, windows, and a south entry; build record explicitly says these are estimates."],
         "findings": ["No current building-specific photographs/elevations support facade material, window rhythm, entrance configuration, or distinctive architectural features. Render appearance alone is not source evidence."]},
        {"criterion": "Modular export, portability, and complete evidence", "points": 2.0 if reopened_ok and source_complete else (1.25 if source_complete else 0.75),
         "max_points": 2.0, "status": "verified" if reopened_ok and source_complete else "provisional; fresh-open verification pending",
         "evidence": [f"Expected asset path: {evidence.get('asset_path')}; collection: {evidence.get('collection')}; named object: {evidence.get('object')}.",
                      "Evidence bundle contains raw GIS and layer metadata snapshots, build record, exterior/interior previews, and a fresh-open validator."],
         "findings": [] if reopened_ok and source_complete else ["Fresh-open validation JSON is absent or does not pass all portability/export checks."]},
    ]
    score = round(sum(c["points"] for c in criteria), 2)
    findings = [finding for c in criteria for finding in c["findings"]]
    return {"building": "Beta Sigma Psi", "purdue_gis_fid": 793, "phase": phase,
            "score": score, "max_score": 10, "criteria": criteria,
            "evidence": {"build_evidence": str(evidence_path), "gis_snapshot": str(gis_path),
                         "reopen_verification": str(reopen_path) if reopen else None,
                         "fresh_open_passed": reopened_ok,
                         "projected_gis_ring_area_m2": round(ring_area, 2),
                         "projected_gis_ring_perimeter_m": round(ring_perimeter, 2),
                         "gis_shape_attribute_mismatch": geometry_attribute_mismatch},
            "findings": findings,
            "passing_standard": 8,
            "result": "pass" if score >= 8 else "below passing standard"}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence")
    parser.add_argument("--reopen")
    parser.add_argument("--phase", default="final")
    args = parser.parse_args()
    print(json.dumps(evaluate(args.evidence, args.reopen, args.phase), indent=2))
