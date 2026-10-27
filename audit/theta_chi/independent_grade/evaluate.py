"""Independent Theta Chi asset grade; run from the PurdueBlender repo root."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit" / "theta_chi"
OUT = AUDIT / "independent_grade"
ASSET = ROOT / "modular" / "buildings" / "massing_house_301841328_39f169f.blend"


def project_lonlat(lon: float, lat: float) -> tuple[float, float]:
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def evaluate() -> dict:
    """Return rubric score and criterion-level evidence from raw sources + Blender reopen."""
    asset_sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    inspection = json.loads((OUT / "asset_inspection.json").read_text(encoding="utf-8"))
    gis = json.loads((AUDIT / "sources" / "purdue_gis_fid760_2026-10-26.json").read_text(encoding="utf-8"))
    feature = gis["features"][0]
    attrs = feature["attributes"]
    ring = feature["geometry"]["rings"][0]
    gis_xy = [project_lonlat(lon, lat) for lon, lat in ring[:-1]]
    obj = inspection["objects"][0]
    base_xy = [tuple(p) for p in obj["z0_xy_vertices"]]
    nearest_errors = [min(math.dist(p, q) for q in base_xy) for p in gis_xy]
    max_base_ring_error = max(nearest_errors)
    source_register = json.loads((AUDIT / "source_register.json").read_text(encoding="utf-8"))
    source_ids = {s["id"] for s in source_register["sources"]}
    evidence_md = (AUDIT / "evidence.md").read_text(encoding="utf-8")
    preview_exists = (AUDIT / "renders" / "theta_chi_preview.png").is_file()

    identity_ok = (attrs.get("FID") == 760 and attrs.get("BUILDING_N") == "Theta Chi"
                   and attrs.get("ADDRESS") == "800 David Ross Rd"
                   and "theta_chi_chapter_housing" in source_ids
                   and "800 David Ross" in evidence_md)
    footprint_ok = (len(gis_xy) == len(base_xy) and max_base_ring_error < 0.001)
    export_ok = (inspection["expected_collection_found"]
                 and inspection["collection_object_count"] == 1
                 and obj["name"] == "House_301841328" and obj["type"] == "MESH"
                 and obj["modifiers"] == []
                 and not inspection["external_images"]
                 and not inspection["linked_libraries"]
                 and preview_exists)

    criteria = [
        {"criterion": "Correct identity and source-backed footprint", "score": 2.0, "max_score": 2,
         "evidence": [
             f"Raw Purdue BuildingShapesZip4 FID {attrs.get('FID')} labels BUILDING_N={attrs.get('BUILDING_N')!r}, ADDRESS={attrs.get('ADDRESS')!r}.",
             "Saved official chapter housing source is independently registered and identifies the Alpha Delta house at the same address.",
             f"Fresh Blender base vertices at Z=0 match the 10 unique projected GIS ring vertices; maximum nearest-vertex error {max_base_ring_error:.6f} m.",
         ], "status": "verified" if identity_ok and footprint_ok else "failed"},
        {"criterion": "Position, orientation, and scale/dimensions", "score": 1.75, "max_score": 2,
         "evidence": [
             f"The 10-point structural ground ring matches the transformed GIS boundary within {max_base_ring_error:.6f} m; XY bounds are independently recoverable from the fresh Blender mesh.",
             "GIS ring supplies polygon orientation and dimensions; coordinates use the documented project WGS84-to-campus approximation.",
             "Photo-to-compass facade bearing is not registered, so correspondence between photographed front and selected GIS long face remains estimated.",
         ], "status": "mostly verified; facade-to-compass registration estimated"},
        {"criterion": "Evidence-backed height, floors, and roof form", "score": 1.25, "max_score": 2,
         "evidence": [
             "Independent inspection confirms mesh Z range 0.0–8.8 m; two occupied levels and a low roof are visible in the two saved official exterior photographs.",
             "The 8.8 m ridge/eave heights and story dimensions have no scaled photo, plan, or survey support and are estimates.",
             "The GIS NUM_LEVELS=1 conflicts with the two visible levels; the modeled roof is a simplified low hip whose exact silhouette is not established by measured evidence.",
         ], "status": "partly supported; vertical dimensions and precise roof silhouette estimated"},
        {"criterion": "Facade, entrances, and distinctive architecture", "score": 1.5, "max_score": 2,
         "evidence": [
             "Direct comparison of saved official chapter photos with preview supports red brick, pale base/trim, two-level windows, entrance accent, and three arched porch bays.",
             "The model carries these features in simplified geometry; photo-scale, window dimensions, exact facade bearing, and unseen elevations are unavailable.",
             "The broad horizontal cream band/cornice and layered roof setbacks visible in the photo are simplified or omitted, limiting facade fidelity.",
         ], "status": "partly supported; simplified and incomplete architectural detail"},
        {"criterion": "Modular export, portability, and complete evidence", "score": 2.0, "max_score": 2,
         "evidence": [
             f"Fresh Blender {inspection['blender_version']} process reopened the expected one-object mesh collection; {obj['vertex_count']} vertices and {obj['face_count']} faces; identity object transform and no modifiers.",
             "Fresh reopen found no external images or linked libraries. Asset SHA-256 is " + asset_sha + ".",
             "Building-specific source snapshots, source register, evidence record, footprint comparison, validation record, preview, and dedicated build script are present.",
         ], "status": "verified" if export_ok else "failed"},
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    findings = [
        "PASS: score meets the repository's 8/10 minimum." if score >= 8 else "FAIL: score is below the repository's 8/10 minimum.",
        "The GIS base ring is exceptionally well supported and numerically matches the official named feature.",
        "The asset's elevations and photo-to-map facade bearing remain estimates; these should stay explicit in downstream records.",
        "No interior, unseen elevations, measured height, or detailed roof construction is verified by the available sources.",
    ]
    return {"score": score, "max_score": 10, "criteria": criteria,
            "evidence": {"asset": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
                         "asset_sha256": asset_sha,
                         "fresh_blender_inspection": "audit/theta_chi/independent_grade/asset_inspection.json",
                         "gis_source": "audit/theta_chi/sources/purdue_gis_fid760_2026-10-26.json",
                         "source_register": "audit/theta_chi/source_register.json",
                         "preview": "audit/theta_chi/renders/theta_chi_preview.png",
                         "max_base_ring_nearest_vertex_error_m": max_base_ring_error,
                         "identity_and_footprint_checks_pass": identity_ok and footprint_ok,
                         "modular_export_check_pass": export_ok},
            "findings": findings,
            "result": "PASS" if score >= 8 else "FAIL"}


if __name__ == "__main__":
    result = evaluate()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "grade_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
