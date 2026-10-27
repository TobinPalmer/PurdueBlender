"""Independent Phi Kappa Tau massing grade for the frozen asset revision."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GRADE = Path(__file__).resolve().parent
ASSET = ROOT / "modular/buildings/massing_phi_kappa_tau_139b9d7.blend"
EXPECTED_SHA256 = "e7eebb66a482d8ef30b3caff2d59aa43ea6f17dab6422ac30ff4c23b9f8a74ee"


def evaluate() -> dict:
    digest = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise RuntimeError(f"Candidate changed: expected {EXPECTED_SHA256}, got {digest}")

    log = (GRADE / "independent_reopen.log").read_text(encoding="utf-8")
    match = re.search(r"(\{\s*\"independent_fresh_reopen\".*?\n\})\s*\nBlender ", log, re.S)
    if not match:
        raise RuntimeError("Could not parse fresh Blender reopen evidence")
    reopened = json.loads(match.group(1))
    if not reopened.get("independent_fresh_reopen") or reopened.get("blender_version") != "5.2.3 LTS":
        raise RuntimeError("Independent Blender reopen did not pass")
    if reopened.get("fid820_ring_max_nearest_error_m", 1) >= 0.01:
        raise RuntimeError("FID820 footprint correspondence exceeds 1 cm")
    if reopened.get("nonmanifold_edges") != 0 or reopened.get("loose_edges") != 0:
        raise RuntimeError("Mesh integrity checks failed")

    crosswalk = (ROOT / "audit/phi_kappa_tau/crosswalk_findings.md").read_text(encoding="utf-8")
    fid820 = json.loads((ROOT / "audit/phi_kappa_tau/fid820_arcgis_snapshot.json").read_text(encoding="utf-8-sig"))
    f820 = next(f for f in fid820["features"] if f["attributes"].get("FID") == 820)
    attrs = f820["attributes"]
    official = (ROOT / "audit/phi_kappa_tau/pkt_house_page.html").read_text(encoding="utf-8").lower()
    alumni = (ROOT / "audit/phi_kappa_tau/phi_chapter_alumni_page.html").read_text(encoding="utf-8").lower()
    psi = (ROOT / "audit/phi_kappa_tau/phi_kappa_psi_contact_page.html").read_text(encoding="utf-8").lower()
    assert attrs.get("BUILDING_N") == "Theta Tau" and attrs.get("ADDRESS") == "416 Chauncey"
    assert "416 n chauncey ave" in official and "now affiliated with phi kappa tau lambda chapter" in alumni
    assert "1307 tower dr" in psi
    assert "fid 856" in crosswalk.lower() and "fid 820" in crosswalk.lower()

    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "points": 1.9,
            "max_points": 2,
            "evidence": "Independent cross-check of raw Purdue BuildingShapes FID 820: historical BUILDING_N=Theta Tau and ADDRESS=416 Chauncey; current Phi Kappa Tau chapter House page names 416 N Chauncey; Phi Chapter alumni history states the house is now affiliated with Phi Kappa Tau Lambda. FID856 instead has 1307 Tower Dr, also named by the official Phi Kappa Psi contact page. The FID820 ring is encoded in the candidate structural shell; independently measured max vertex error is 0.000019 m.",
            "finding": "The assignment correction from FID856 to FID820 is well supported by address, house-transition history, and geometry. The historic GIS name requires the documented crosswalk; FID820 is not labeled Phi Kappa Tau in the GIS itself."
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "points": 1.9,
            "max_points": 2,
            "evidence": "Candidate wall plan is traced from all six vertices of the raw FID820 polygon, transformed from EPSG:3857 with the repository's published local approximation. Independent reopened bounds: X 584.108–600.960 m, Y 78.464–108.641 m, Z 0–10.350 m; the slight horizontal extent beyond the wall ring comes from the portico, trim, and roof overhang. Structural ring vertex match is within 0.000019 m.",
            "finding": "The project conversion is approximate, and no survey control or independently measured facade dimensions are available. Position is verified relative to this GIS source, not a ground survey."
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "points": 1.2,
            "max_points": 2,
            "evidence": "The current chapter exterior photo supports a two-level brick facade, pitched dark roof, and four attic dormer/gable projections. The county parcel snapshot gives year built 2002 and 9,918 sq ft finished area, but does not validate floor count or height. Candidate has a 6.67 m wall shell and 10.35 m max overall height, both explicitly estimated.",
            "finding": "No elevations, sections, LiDAR roof sample, or verified height source was found. Roof silhouette is simplified: the photo's outer dormer/gable projections are substantially larger than the four equal compact dormers modeled. Actual heights, attic configuration, and pitch remain unverified."
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "points": 1.3,
            "max_points": 2,
            "evidence": "The candidate reproduces photo-supported red/brown brick, light stone bands and corner quoins, repeated windows, a west-facing columned entry portico, and dark roof with dormers. The House page photo and the recent group photo at 416 N Chauncey independently identify the current chapter house and its brick/stone facade and columned entry.",
            "finding": "The candidate reads as a credible massing, but window bay widths, course spacing, dormer sizes, column count, portico proportions, and exact entrance offset are estimates. Relative to the official facade image, the large projecting dormer bays and facade articulation are under-modeled; no measured elevations or facade drawings support exact detail."
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "points": 2.0,
            "max_points": 2,
            "evidence": "Frozen asset SHA256 matches the requested exact revision. Independent Blender 5.2.3 fresh-process reopen found the expected scene, stable asset ID, named collection, single mesh object and identity transform; 1,794 vertices, 2,691 edges, 1,323 faces, zero nonmanifold edges, zero loose edges, seven named materials, and no external images. Raw GIS snapshots, official source page snapshots, build validation, renders, and this independent reopen record are present.",
            "finding": "The shared manifest and master-blend integration were not in this grading scope; root coordinator must update and integrate after the builder's commit."
        }
    ]
    score = round(sum(c["points"] for c in criteria), 2)
    result = {
        "score": score,
        "max_score": 10,
        "pass": score >= 8,
        "criteria": criteria,
        "evidence": {
            "candidate_path": "modular/buildings/massing_phi_kappa_tau_139b9d7.blend",
            "stable_asset_id": "massing_phi_kappa_tau_139b9d7",
            "candidate_sha256": digest,
            "fresh_reopen": reopened,
            "crosswalk_sources": [
                {"url": "https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0", "provider": "Purdue BuildingShapes", "feature_id": 820, "source_crs": "EPSG:3857 (WKID 102100)", "snapshot": "audit/phi_kappa_tau/fid820_arcgis_snapshot.json", "retrieved": "2026-10-26"},
                {"url": "https://www.phikappataupurdue.com/house/", "provider": "Phi Kappa Tau Purdue Lambda chapter", "evidence": "416 N Chauncey address and exterior photo", "snapshot": "audit/phi_kappa_tau/pkt_house_page.html", "retrieved": "2026-10-26"},
                {"url": "https://phikappatorque.com/torque", "provider": "Phi Chapter alumni association", "evidence": "historic house at 416 N Chauncey; now affiliated with Phi Kappa Tau Lambda", "snapshot": "audit/phi_kappa_tau/phi_chapter_alumni_page.html", "retrieved": "2026-10-26"},
                {"url": "https://purdue.phikappapsi.com/contact", "provider": "Phi Kappa Psi Indiana Delta chapter", "evidence": "1307 Tower Dr corroborates the FID856 location conflict", "snapshot": "audit/phi_kappa_tau/phi_kappa_psi_contact_page.html", "retrieved": "2026-10-26"}
            ],
            "supporting_artifacts": ["audit/phi_kappa_tau/crosswalk_findings.md", "audit/phi_kappa_tau/county_parcel_416_chauncey.json", "audit/phi_kappa_tau/preview_phi_kappa_tau.png", "audit/phi_kappa_tau/preview_phi_kappa_tau_top.png", "audit/phi_kappa_tau/pkt_house_416_chauncey.png", "audit/phi_kappa_tau/new_letters_at_416_chauncey.jpg", "audit/phi_kappa_tau/independent_grade/independent_reopen.py", "audit/phi_kappa_tau/independent_grade/independent_reopen.log"]
        },
        "findings": [
            "PASS at 8.3/10. The corrected FID820 identity, source-derived structural plan, and modular Blender asset integrity are supported by direct independent checks.",
            "The grade is for the standalone massing asset only. It does not verify campus-master integration.",
            "Roof and height remain visibly and quantitatively estimated; major dormer/gable projections in the official photo are simplified in the candidate."
        ],
        "grader": "independent evidence review and Blender 5.2.3 reopen",
        "date": "2026-10-26"
    }
    if score != 8.3:
        raise RuntimeError(f"Unexpected criterion sum: {score}")
    out = GRADE / "independent_grade_result.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
