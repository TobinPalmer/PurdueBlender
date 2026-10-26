"""Independent Alpha Chi Rho source/model scorecard. Run with Python 3."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "alpha_chi_rho"
OUT = Path(__file__).resolve().parent
BLENDER = Path(r"C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\blender\blender-4.5.15-windows-x64\blender.exe")
ASSET = ROOT / "modular" / "buildings" / "massing_alpha_chi_rho_0cb591a.blend"


def evaluate():
    """Open the asset in Blender, compare evidence records, and return scorecard."""
    assert BLENDER.is_file() and ASSET.is_file()
    subprocess.run([str(BLENDER), "--background", str(ASSET), "--python",
                    str(OUT / "probe_asset.py")], check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    probe = json.loads((OUT / "asset_probe.json").read_text(encoding="utf-8"))
    build = json.loads((AUDIT / "build_evidence.json").read_text(encoding="utf-8"))
    comparison = json.loads((AUDIT / "footprint_comparison.json").read_text(encoding="utf-8"))
    street = json.loads((AUDIT / "sources" / "streetview_source_record.json").read_text(encoding="utf-8"))
    gis = json.loads((AUDIT / "sources" / "purdue_gis_FID775_alpha_chi_rho_2026-10-26.json").read_text(encoding="utf-8"))
    validation = json.loads((AUDIT / "reopen_validation.json").read_text(encoding="utf-8"))
    export = json.loads((AUDIT / "export_reopen_probe.json").read_text(encoding="utf-8"))

    attrs = gis["features"][0]["attributes"]
    assert attrs["FID"] == 775 and attrs["BUILDING_N"] == "Alpha Chi Rho"
    assert probe["asset_object_count"] == 1 and probe["object_type"] == "MESH"
    assert probe["mesh_vertices"] == validation["mesh_vertices"]
    assert validation["status"] == "PASS" and export["status"] == "PASS"
    iou = comparison["raster_intersection_over_union"]
    center_offset = comparison["centroid_separation_m"]
    min_z, max_z = probe["world_bounds_m"][2]
    street_inspection = {
        "provider": "Google Street View",
        "address": "27 N Russell St, West Lafayette, Indiana",
        "panorama_id": street["panorama_id"],
        "url": street["page_url"],
        "independently_observed_capture_date": "Aug 2019",
        "observation_method": "Opened the address-matched panorama in Chrome and read the Google Street View capture label; visually compared facade and roof silhouette with the revised preview.",
        "visible_features": [
            "two visible stories",
            "light horizontal siding with dark maroon shutters",
            "centered tall portico with columns, balcony railing, and central entry",
            "triangular gable above the portico and a low roofline behind it",
            "front steps and a broad regular window rhythm"
        ],
        "model_comparison": "The asset represents the two-story mass, siding, shutters, centered entry/portico, balcony and gable. The primary roof is simplified to a flat cap, exact openings and dimensions differ or remain illustrative, and stairs/entry ornament are omitted.",
        "date_limit": "This verifies the panorama date as Aug 2019, not the building's 2026 condition."
    }
    (OUT / "streetview_inspection.json").write_text(
        json.dumps(street_inspection, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint", "points": 1.9, "max_points": 2,
            "evidence": [
                "Purdue BuildingShapes feature FID 775 names Alpha Chi Rho (SOACR) at 27 Russell St and provides the footprint used by the model.",
                f"The reopened asset retains the source ring to {validation['shell_footprint_max_vertex_error_m']:.6f} m vertex error.",
                f"Independent Indiana 2018 LiDAR footprint 410090 has raster IoU {iou:.3f} and centroid separation {center_offset:.3f} m against the Purdue polygon; it broadly corroborates location and shape, while edge disagreement remains material."
            ],
            "deduction": "The independent outline is LiDAR-derived, not a site survey; its IoU of about 0.785 leaves boundary differences unresolved."
        },
        {
            "criterion": "Position, orientation, and scale/dimensions", "points": 1.7, "max_points": 2,
            "evidence": [
                f"Purdue and Indiana footprints have centroids only {center_offset:.3f} m apart.",
                "The asset's horizontal outline matches the Purdue feature in its documented campus-local conversion; the independent outline supports broad registration and scale.",
                "The repository conversion is an approximate lon/lat-to-local-meter transform, not surveyed geodetic control."
            ],
            "deduction": "No surveyed control confirms absolute placement; the two footprint products differ at the edges."
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form", "points": 1.15, "max_points": 2,
            "evidence": [
                f"The saved model spans Z={min_z:.2f} to {max_z:.2f} m, with a documented 6.2 m estimated wall height and 7.62 m estimated high point.",
                "Google's Aug 2019 Street View supports two visible stories; Purdue GIS reports one level, and no measured elevation or roof plan is supplied.",
                "Zillow's asphalt-roof claim does not establish the modeled roof geometry."
            ],
            "deduction": "Vertical dimensions and story spacing are estimates, the GIS level count conflicts with the visual story count, and the model simplifies the visible roof profile to a flat cap."
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture", "points": 1.4, "max_points": 2,
            "evidence": [
                "Direct review of the address-matched panorama shows a two-story light-sided facade, dark shutters, centered tall portico/balcony, entry and gable; these broad features appear in the revised model.",
                "Google labels the image Aug 2019. It supports the facade as of that date, not current condition or exact opening arrangement.",
                "The model simplifies the main roof, window rhythm, entry steps and ornament.",
                "The 1978 Purdue Debris record is historical context only and does not validate the present facade."
            ],
            "deduction": "Street-level image supports broad character as of Aug 2019; exact openings and dimensions remain illustrative, and several visible details are simplified."
        },
        {
            "criterion": "Modular export, portability, and complete evidence", "points": 2.0, "max_points": 2,
            "evidence": [
                f"A fresh Blender 4.5.15 open probe found the expected collection with {probe['asset_object_count']} mesh object ({probe['mesh_vertices']} vertices, {probe['mesh_polygons']} polygons).",
                "Builder reopen validation and clean-scene append/save/reopen portability probe both report PASS.",
                f"No external image dependencies are present; {len(probe['material_names'])} materials are embedded and building-specific evidence records include source identifiers, URLs, dates, CRS/method notes and uncertainty."
            ],
            "deduction": None
        }
    ]
    score = round(sum(item["points"] for item in criteria), 2)
    findings = [
        {"severity": "moderate", "finding": "The footprint match has a measurable edge discrepancy: the independent 2018 LiDAR outline and Purdue GIS outline have only about 0.785 raster IoU.", "recommended_evidence": "Check a georeferenced current orthophoto or survey to decide which perimeter represents the above-ground structure."},
        {"severity": "moderate", "finding": "The 6.2 m wall height and roof dimensions are estimated, and GIS's one-level attribute conflicts with two stories visible in Street View.", "recommended_evidence": "Find a dimensioned elevation or dated campus imagery with a scale reference; preserve the height as estimated until then."},
        {"severity": "minor", "finding": "The Street View panorama is dated Aug 2019 and cannot establish the building's current 2026 condition.", "recommended_evidence": "Seek a dated current facade photograph if exact present condition matters."}
    ]
    return {
        "asset": "modular/buildings/massing_alpha_chi_rho_0cb591a.blend",
        "building_id": "massing_alpha_chi_rho_0cb591a",
        "independent_grade": True,
        "score": score,
        "max_score": 10,
        "pass_threshold": 8,
        "status": "PASS" if score >= 8 else "FAIL",
        "criteria": criteria,
        "evidence": {
            "asset_probe": "audit/alpha_chi_rho_independent_grade_r2/asset_probe.json",
            "purdue_source": "audit/alpha_chi_rho/sources/purdue_gis_FID775_alpha_chi_rho_2026-10-26.json",
            "indiana_source": "audit/alpha_chi_rho/sources/indiana_lidar_building_footprint_410090_2026-10-26.json",
            "footprint_comparison": "audit/alpha_chi_rho/footprint_comparison.json",
            "streetview_source_record": "audit/alpha_chi_rho/sources/streetview_source_record.json",
            "direct_streetview_inspection": "audit/alpha_chi_rho_independent_grade_r2/streetview_inspection.json",
            "build_evidence": "audit/alpha_chi_rho/build_evidence.json",
            "reopen_validation": "audit/alpha_chi_rho/reopen_validation.json",
            "portable_export_probe": "audit/alpha_chi_rho/export_reopen_probe.json",
            "preview": "audit/alpha_chi_rho/alpha_chi_rho_preview.png"
        },
        "findings": findings,
        "remaining_uncertainty": [
            "Whether the Purdue outline precisely traces the current above-ground perimeter; the 2018 LiDAR outline differs at the edges.",
            "Absolute horizontal registration accuracy of the approximate local-coordinate transform.",
            "Measured wall/eave height, vertical datum, roof plan/profile, and exact facade dimensions.",
            "The 2019 Street View image cannot establish current 2026 condition."
        ],
        "rubric_note": "Scores reflect source-backed correctness rather than appearance. The dated 2019 Street View was directly reviewed; its age, estimated dimensions, simplified roof, and footprint-edge disagreement are explicitly deducted."
    }


if __name__ == "__main__":
    result = evaluate()
    (OUT / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"score": result["score"], "max_score": result["max_score"],
                      "status": result["status"], "criteria": result["criteria"],
                      "findings": result["findings"]}, indent=2, ensure_ascii=False))
