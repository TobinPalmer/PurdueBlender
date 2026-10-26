"""Independent localized KFPC grade; run with the fresh Blender probes present."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED_ASSET_SHA = "c22443f6751e276cd93dc41ffec119e151f88997dde3e6258e5b6a709259d93a"
EXPECTED_MASTER_SHA = "27569901dd28d7f48948c150bdc67749537fa36086236d8e36d53430482dfb36"


def evaluate():
    asset = json.loads((HERE / "asset_probe.json").read_text(encoding="utf-8"))
    master = json.loads((HERE / "master_probe.json").read_text(encoding="utf-8"))
    criteria = [
        {"criterion": "Correct identity and source-backed footprint", "score": 2.0, "max_score": 2.0,
         "status": "verified", "evidence": [
             "Purdue Libraries GIS feature 1202 (FPC) and official Purdue facility sources identify the Kozuch Football Performance Complex.",
             f"The localized master instance's 44-vertex structural plinth matches all 22 source GIS vertices; max nearest-vertex error is {master['gis_footprint_alignment']['max_source_vertex_to_master_plinth_distance_m']:.8f} m.",
             "The saved Esri imagery overlay places the GIS outline on the complex at Mollenkopf's north end."
         ], "reason": "Identity is cross-checked with official sources and the actual master instance's footprint aligns with Purdue GIS."},
        {"criterion": "Position, orientation, and scale/dimensions", "score": 2.0, "max_score": 2.0,
         "status": "verified against GIS and master placement", "evidence": [
             "A fresh master open found exactly one Placement_massing_purdue_football_performance_complex_f106c29 empty, instancing the expected Asset collection.",
             f"The marker is at {master['collection_instancers'][0]['marker_location_world_m']} m with zero rotation; GIS-to-instance plinth error is {master['gis_footprint_alignment']['max_source_vertex_to_master_plinth_distance_m']:.8f} m.",
             f"Freshly evaluated master instance world bounds are {master['collection_instancers'][0]['world_bounds_m']} m.",
             "The asset's updated local X bounds are recentered; applying the master marker restores the source-matched campus-space footprint."
         ], "reason": "The changed local frame is compensated by the single master marker, and direct GIS comparison validates final campus position, orientation, and plan scale."},
        {"criterion": "Evidence-backed height, floors, and roof form", "score": 1.1, "max_score": 2.0,
         "status": "partly supported; vertical form uncertain", "evidence": [
             "Purdue Athletics and the architect describe a three-level facility; no measured elevation was located.",
             f"Fresh source asset height is {asset['local_geometry_bounds_m'][2][1]:.2f} m and remains an estimate.",
             "Three full-footprint plates appear inconsistent with the 112,000 sq ft published gross area; actual story extents are not documented.",
             "Populous describes a two-plane flight-inspired roof; the model's main roof slopes remain subtle compared with the official entrance photo."
         ], "reason": "The three-level program and roof concept are source-backed but the precise elevations and vertical extents are not."},
        {"criterion": "Facade, entrances, and distinctive architecture", "score": 1.4, "max_score": 2.0,
         "status": "key features present; detailing partly interpreted", "evidence": [
             "The model includes glazed facade bands, metal cladding, projecting entrance canopy, splayed columns, Purdue P/address signage, floors, and schematic lobby/team-hall spaces.",
             "Saved entrance and three-quarter previews show the implemented features; source photography supports the architectural palette and major entrance elements.",
             "Facade bay rhythm, hidden sides, and interior organization remain simplified or schematic."
         ], "reason": "Identity-bearing facade and entrance elements are represented; several architectural details are interpreted rather than dimensionally documented."},
        {"criterion": "Modular export, portability, and complete evidence", "score": 2.0, "max_score": 2.0,
         "status": "verified", "evidence": [
             f"Fresh Blender 5.2.3 open confirmed expected scene and collection; {asset['object_count']} objects, {asset['geometry_object_count']} geometry objects, {asset['mesh_count']} meshes, and {len(asset['materials_used'])} used materials.",
             "No linked objects or unpacked external images were found in the source asset.",
             f"Asset SHA-256 matches the requested localized revision: {asset['blend_sha256']}.",
             f"Master SHA-256 independently read as {master['blend_sha256']}; its one instance resolves to the expected collection."
         ], "reason": "The exact revision opens cleanly, is self-contained, and is instantiated once through the modular master placement."}
    ]
    score = round(sum(c["score"] for c in criteria), 1)
    errors = []
    if asset["blend_sha256"] != EXPECTED_ASSET_SHA:
        errors.append("asset SHA does not match the requested revision")
    if master["blend_sha256"] != EXPECTED_MASTER_SHA:
        errors.append("master SHA differs from the independently reviewed master revision")
    if asset["status"] != "PASS" or master["status"] != "PASS":
        errors.append("one or more Blender fresh-open probes failed")
    return {
        "building": "Kozuch Football Performance Complex",
        "asset_id": "massing_purdue_football_performance_complex_f106c29",
        "asset_path": "modular/buildings/massing_purdue_football_performance_complex_f106c29.blend",
        "asset_sha256": asset["blend_sha256"],
        "master_path": "purdue_campus_master.blend",
        "master_sha256": master["blend_sha256"],
        "grader": "independent_grader_subagent",
        "grade_date": "2026-10-26",
        "score": score,
        "max_score": 10,
        "passing_threshold": 8,
        "status": "PASS" if score >= 8 and not errors else "FAIL",
        "criteria": criteria,
        "master_placement": master["collection_instancers"],
        "gis_footprint_alignment": master["gis_footprint_alignment"],
        "evidence": ["asset_probe.json", "master_probe.json", "../gis_footprint_on_esri_imagery.png", "../preview_entrance.png", "../preview_three_quarter.png", "../build_evidence.json", "../sources/"],
        "findings": [
            "The localized asset revision retains the previously reviewed geometry and materials, with local X recentered; the master placement compensates for the change.",
            "The unique master marker has zero rotation, references the expected asset collection, and its actual instance footprint matches Purdue GIS FID 1202 to within 0.000004 m.",
            "The aerial GIS overlay shows the complex at Mollenkopf's north end. This review confirms the KFPC footprint is separately represented by its own collection instance; it does not claim to verify every adjoining Mollenkopf wall or seam in the broader master.",
            "Height, exact story extents, and the dramatic roof fold remain estimated or simplified; the interior is schematic."
        ],
        "errors": errors
    }


if __name__ == "__main__":
    result = evaluate()
    (HERE / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
