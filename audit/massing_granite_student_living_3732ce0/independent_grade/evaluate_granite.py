#!/usr/bin/env python3
"""Independent, read-only rubric evaluation for the Granite Student Living asset."""
from __future__ import annotations

import json
import math
from pathlib import Path


ASSET_ID = "massing_granite_student_living_3732ce0"
HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent
ROOT = AUDIT.parents[1]


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def evaluate() -> dict:
    """Score evidence against five two-point criteria; no model/source edits."""
    register = load_json(AUDIT / "source_register.json")
    reopen = load_json(AUDIT / "reopen_validation.json")
    orthophoto = load_json(AUDIT / "orthophoto_measurement.json")
    prebuild = load_json(AUDIT / "prebuild_geometry_snapshot.json")
    manifest = load_json(ROOT / "modular" / "manifest.json")
    asset = next((a for a in manifest["assets"] if a.get("id") == ASSET_ID), None)
    source_by_id = {s["id"]: s for s in register["sources"]}

    structural = reopen["structural_block_bounds_m"]
    dims = [round(b[1] - b[0], 3) for b in structural]
    center = [round((b[0] + b[1]) / 2, 3) for b in structural]
    origin = manifest["origin"]
    geocoder = load_json(AUDIT / "sources" / "indiana_composite_geocoder_225_northwestern_2026-10-26.json")
    candidates = [c for c in geocoder.get("candidates", []) if c.get("score") == 100]
    # Use the project's documented local approximation. Candidate ambiguity is
    # retained in the assessment; this is not a surveyed placement check.
    errors = []
    for candidate in candidates:
        loc = candidate["location"]
        x = (loc["x"] - origin["lon"]) * origin["longitude_to_meters"]
        y = (loc["y"] - origin["lat"]) * origin["latitude_to_meters"]
        errors.append(round(math.hypot(x - center[0], y - center[1]), 2))

    collection_name = "Asset_" + ASSET_ID
    manifest_match = bool(asset and asset.get("file") == f"buildings/{ASSET_ID}.blend"
                          and asset.get("collection") == collection_name)
    source_files = [s.get("snapshot") for s in register["sources"] if s.get("snapshot")]
    raw_snapshot_exists = {name: (AUDIT / name).is_file() for name in source_files}
    expected_export = reopen.get("collection") == collection_name and reopen.get("checks", {}).get("expected_collection")
    complete_reopen = expected_export and reopen.get("checks", {}).get("single_expected_asset_collection")
    portable = (reopen.get("checks", {}).get("portable_materials")
                and not reopen.get("checks", {}).get("textures_external")
                and not reopen.get("relative_libraries"))

    scores = [1.25, 1.0, 1.0, 0.75, 2.0]
    criteria = [
        {"name": "Correct identity and source-backed footprint", "score": scores[0], "max_score": 2,
         "assessment": "Identity is supported; footprint shape and exact wall edge remain unverified.",
         "evidence": [
             "Operator listing identifies North by Northwest at 225 Northwestern Ave.",
             "Architect description and county-hosted market survey also associate 225 Northwestern with North by Northwest.",
             "Current orthophoto gives an approximate elongated roof envelope (18.0 x 51.6 m), but it is a roof-edge estimate, not a wall footprint.",
             "Indiana 2016-2020 building-footprint query returned no polygon intersecting this asset envelope; exact footprint is not GIS-verified.",
         ]},
        {"name": "Position, orientation, and scale/dimensions", "score": scores[1], "max_score": 2,
         "assessment": "Position is plausible and scale is broadly consistent with imagery; exact position/orientation are unverified.",
         "evidence": [
             f"Saved structural bounds are approximately {dims[0]} x {dims[1]} x {dims[2]} m, center {center} m in campus coordinates.",
             f"Center-to-each of {len(candidates)} equally scored (100) address candidates is {errors} m using the documented local approximation.",
             "Orthophoto roof length estimate differs from the saved structural length by about 5.3 m; roof edge and wall footprint are not interchangeable.",
             "No matching surveyed footprint or street-address parcel point establishes exact rotation or wall dimensions.",
         ]},
        {"name": "Evidence-backed height, floors, and roof form", "score": scores[2], "max_score": 2,
         "assessment": "Five-level count and hipped roof have partial independent support; numeric height and detailed roof geometry are estimates.",
         "evidence": [
             "Model has one 3.85 m ground level and four repeated residential levels, with roof ridge at 16 m overall.",
             "ForRent profile describes five stories, while a property-photo caption reportedly calls the building four-story; floor count remains conflicting/estimated.",
             "Current orthophoto supports a hipped roof silhouette, but the model's simple low-pitch hip is not validated against final elevations or plans.",
             "No source provides verified elevation heights or measured floor-to-floor dimensions.",
         ]},
        {"name": "Facade, entrances, and distinctive architecture", "score": scores[3], "max_score": 2,
         "assessment": "The broad material and balcony language is supported, but exact facade rhythm and entrance layout are weakly documented.",
         "evidence": [
             "Preview shows red brick, pale stone base/corner accents, dark windows, black balcony rails, and red awnings.",
             "Source register attributes red brick, pale stone accents, black balcony rails, red ground-level awnings, and apartment window rhythm to a PurdueGuru property photo.",
             "That photo is not included as a raw local snapshot in the supplied evidence folder, limiting independent source inspection.",
             "Operator listing supports balconies but does not establish exact bay spacing, number of bays, storefront positions, or residential entrance placement.",
         ]},
        {"name": "Modular export, portability, and complete evidence", "score": scores[4], "max_score": 2,
         "assessment": "Export and file portability checks pass; evidence is structured and limitations are documented.",
         "evidence": [
             f"Reopened asset reports {reopen.get('collection_objects')} collection objects and {reopen.get('mesh_objects')} meshes in the expected collection.",
             f"Manifest ID/path/collection match: {manifest_match}; reopen expected-collection/single-collection checks: {complete_reopen}.",
             f"Portable material check passes: {portable}; no external linked libraries and no external textures are reported.",
             f"Source register, orthophoto measurement, prebuild snapshot, reopen validation, and exterior/end-view renders are present; registered raw snapshots present: {raw_snapshot_exists}.",
         ]},
    ]
    findings = [
        "Exact structural footprint and orientation remain unverified because the queried GIS footprint source did not match the building.",
        "Geocoder center agreement is approximate and ambiguous: multiple 100-score candidates exist for this address.",
        "The five-story model is plausible but floor count conflicts across secondary sources; exact height is unsupported.",
        "The saved facade reference photo is not present as a raw snapshot, and detailed storefront/entrance locations are not independently established.",
        "The imagery's roof-length estimate is about 5.3 m longer than the retained structural length; the discrepancy is unresolved because imagery measures roof edges.",
    ]
    result = {
        "building_id": ASSET_ID,
        "score": round(sum(c["score"] for c in criteria), 2),
        "max_score": 10,
        "passing_standard": 8,
        "criteria": criteria,
        "evidence": {
            "asset_file": reopen.get("file"),
            "collection": reopen.get("collection"),
            "direct_reopen_bounds_m": reopen.get("collection_bounds_evaluated_m"),
            "structural_bounds_m": structural,
            "structural_dimensions_m": dims,
            "structural_center_m": center,
            "candidate_center_errors_m": errors,
            "prebuild_dimensions_m": prebuild.get("objects", [{}])[0].get("dims"),
            "orthophoto_roof_size_approx_m": orthophoto.get("visual_roof_size_approx_m"),
            "manifest_entry_present_and_consistent": manifest_match,
            "source_snapshot_files_present": raw_snapshot_exists,
        },
        "findings": findings,
    }
    return result


if __name__ == "__main__":
    report = evaluate()
    destination = HERE / "result.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"score": report["score"], "max_score": report["max_score"],
                      "findings": report["findings"], "result_file": str(destination)}, indent=2))
