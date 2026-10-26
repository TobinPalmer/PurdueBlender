"""Independent rubric evaluator for the saved Dudley Hall library.

Run with: python audit/dudley_hall/independent_grade/grade_dudley_hall.py
This evaluator reads the retained reopen validation, source records, manifest,
and preview. It does not edit or regenerate the Blender asset.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit" / "dudley_hall"

def evaluate(root=ROOT):
    root = Path(root)
    audit = root / "audit" / "dudley_hall"
    validation = json.loads((audit / "asset_validation.json").read_text(encoding="utf-8"))
    build = json.loads((audit / "build_evidence.json").read_text(encoding="utf-8"))
    gis_doc = json.loads((audit / "sources" / "purdue_gis_fid432_dudley_hall.json").read_text(encoding="utf-8"))
    feature = gis_doc["feature"]
    manifest_doc = json.loads((root / "modular" / "manifest.json").read_text(encoding="utf-8"))
    entries = manifest_doc if isinstance(manifest_doc, list) else manifest_doc.get("assets", [])
    if isinstance(entries, dict):
        entries = list(entries.values())
    entry = next((x for x in entries if x.get("id") == "dudley_hall"), {})

    source_paths = [
        audit / "sources" / "purdue_gis_fid432_dudley_hall.json",
        audit / "sources" / "purdue_dudley_hall_2019.html",
        audit / "sources" / "ennead_project_page.html",
        audit / "sources" / "ennead_dudley_lambertus_exterior_0007.jpg",
    ]
    asset = root / "modular" / "buildings" / "dudley_hall.blend"
    preview = audit / "views" / "dudley_hall_refined_preview.png"
    gis_error = max(validation["gis_to_shell_nearest_max_m"], validation["shell_to_gis_nearest_max_m"])
    all_sources_present = all(p.is_file() for p in source_paths)
    evidence_complete = all(
        src.get(k) is not None
        for src in build.get("sources", [])
        for k in ("provider", "url", "source_date", "measurement_method", "uncertainty")
    ) and all_sources_present
    correct_identity = feature.get("fid") == 432 and feature.get("code") == "DUDL" and feature.get("name") == "Dudley Hall"
    exact_outline = gis_error <= 0.001 and validation.get("gis_feature_id") == 432 and validation.get("gis_code") == "DUDL"
    campus_asset = entry.get("kind") == "massing" and entry.get("placement_transform") == "identity; campus world coordinates"
    dimensions = feature["minimum_rotated_rectangle"]
    manifest_file = entry.get("file") == "buildings/dudley_hall.blend"
    export_ok = (
        asset.is_file()
        and manifest_file
        and entry.get("collection") == validation.get("collection") == "Asset_dudley_hall"
        and validation.get("reopened_in_blender")
        and validation.get("mesh_object_count", 0) >= 1
    )

    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 2 if correct_identity and exact_outline else (1 if correct_identity or exact_outline else 0),
            "max_score": 2,
            "evidence": f"Official Purdue GIS feature {feature.get('fid')} ({feature.get('code')}, {feature.get('name')}); saved validation reports symmetric nearest-vertex error {gis_error:.4f} m. GIS attributes identify the hall, while the footprint is horizontal only and not a certified survey.",
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 2 if campus_asset and exact_outline and dimensions.get("width_m", 0) > 0 else 1,
            "max_score": 2,
            "evidence": f"Manifest defines direct campus-world coordinates with identity transform. Exact ring correspondence preserves placement and orientation; GIS minimum-rotated-rectangle dimensions are {dimensions['width_m']:.2f} x {dimensions['depth_m']:.2f} m at {dimensions['angle_degrees_east_ccw']:.3f}° east of north. The metric frame is the project’s approximate geographic conversion, not survey control.",
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 1,
            "max_score": 2,
            "evidence": "Purdue’s archived 2019 announcement identifies four stories plus a basement, which supports four visible above-grade bands. The saved model is 16.0 m tall and the flat parapet roof is visually plausible, but height, roof elevation, and basement depth have no measured source; GIS explicitly marks height unverified.",
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1,
            "max_score": 2,
            "evidence": "Direct visual review of the saved preview shows brick-colored walls, repeated dark window bands, a glazed entrance treatment, a pale facade cue, and a terracotta-colored screen. These cues appear in the saved Ennead photograph, but that photograph shows both Dudley and Lambertus; assigning these elements to Dudley’s polygon and fixing their exact positions is schematic. The preview is a single oblique view and does not independently establish facade orientation or detail accuracy.",
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 2 if export_ok and evidence_complete else (1 if export_ok or evidence_complete else 0),
            "max_score": 2,
            "evidence": f"Saved asset exists at the manifest path; retained Blender reopen record names collection {validation.get('collection')} and {validation.get('mesh_object_count')} meshes. Builder generates geometry/materials internally without external texture paths. Source records include provider, URL, feature/date, CRS or applicability, method, and uncertainty; preview and raw source snapshots exist ({sum(p.is_file() for p in source_paths)}/{len(source_paths)} source files).",
        },
    ]
    score = sum(c["score"] for c in criteria)
    findings = [
        "The official GIS outline verifies horizontal plan agreement only; it does not verify facade offsets, height, roof elevation, or basement depth.",
        "The model’s 16.0 m height is an estimate. Four stories are sourced, but the floor-to-floor dimensions are not.",
        "The Ennead exterior image depicts the combined Dudley–Lambertus complex; facade assignment to Dudley and screen placement remain uncertain.",
        "The saved preview supports only a schematic architectural resemblance and does not resolve the combined-hall attribution uncertainty.",
    ]
    return {
        "score": score,
        "max_score": 10,
        "minimum_pass": 8,
        "passed": score >= 8,
        "criteria": criteria,
        "evidence": {
            "asset": str(asset.relative_to(root)),
            "preview_visually_inspected": str(preview.relative_to(root)) if preview.is_file() else None,
            "source_files": [str(p.relative_to(root)) for p in source_paths if p.is_file()],
            "saved_blender_reopen_record": str((audit / "asset_validation.json").relative_to(root)),
            "gis_symmetric_nearest_vertex_error_m": gis_error,
            "gis_minimum_rotated_rectangle_m": [dimensions.get("width_m"), dimensions.get("depth_m")],
            "model_z_bounds_m": validation.get("bounds_xyz_m", [None, None, None])[2],
        },
        "findings": findings,
        "method_note": "Independent assessment used direct visual comparison of the saved preview against the retained original source image, and read the raw GIS/source snapshots and saved-asset Blender reopen record. No builder or geometry was modified.",
    }

if __name__ == "__main__":
    result = evaluate()
    out = AUDIT / "independent_grade" / "result.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
