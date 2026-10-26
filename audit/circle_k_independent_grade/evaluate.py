"""Independent, evidence-driven Circle K massing evaluator (0-10)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "result.json"
probe = json.loads((Path(__file__).resolve().parent / "blender_probe.json").read_text(encoding="utf-8"))
evidence = json.loads((ROOT / "audit" / "circle_k" / "evidence_2026-10-26.json").read_text(encoding="utf-8"))
reopen = json.loads((ROOT / "audit" / "circle_k" / "reopen_validation_2026-10-26.json").read_text(encoding="utf-8"))

criteria = [
    {
        "name": "Correct identity and source-backed footprint",
        "score": 2.0,
        "max_score": 2.0,
        "evidence": [
            "OSM way 345144282 is tagged amenity=fuel, brand/name=Circle K, operator=Mobil, building=retail, building:levels=1, with the station website for 706 Northwestern Avenue.",
            f"Independent Blender reopen compared the 4 OSM vertices with the Circle K shell: symmetric XY Hausdorff error {probe['symmetric_hausdorff_xy_error_m']:.6f} m; shell dimensions {probe['store_shell_dimensions_m'][0]:.3f} x {probe['store_shell_dimensions_m'][1]:.3f} m.",
            "Indiana 2018 LiDAR-derived footprint is an independent spatial cross-check but has a wider jogged boundary; the builder explicitly retained the named OSM store shell and records the mismatch rather than treating the footprint as the same envelope.",
        ],
        "findings": "Identity and the principal store footprint are strongly supported. The adjacent canopy is correctly kept outside the store footprint comparison.",
    },
    {
        "name": "Position, orientation, and scale/dimensions",
        "score": 2.0,
        "max_score": 2.0,
        "evidence": [
            "Store shell XY vertices match OSM transformed with the Purdue origin and documented local meter conversion; its long axis follows the east-west footprint edges.",
            f"Reopened shell center is ({probe['store_shell_center_xy_m'][0]:.3f}, {probe['store_shell_center_xy_m'][1]:.3f}) m in the campus coordinate frame. Esri World Imagery mosaic shows the separate canopy south of the store, in agreement with the model arrangement.",
            "Canopy's 22.6 x 7.6 m footprint and south offset are approximate image measurements, explicitly described as estimates; no measured site plan is present.",
        ],
        "findings": "Store placement and plan are effectively exact to the OSM coordinate source. The station canopy location and size remain imagery estimates, but are plausible and clearly treated as an accessory rather than part of the building shell.",
    },
    {
        "name": "Evidence-backed height, floors, and roof form",
        "score": 1.25,
        "max_score": 2.0,
        "evidence": [
            "OSM tags one building level; the location-identified exterior photos show a one-story store and a low dark pitched roof.",
            f"Saved shell wall height is {probe['store_shell_dimensions_m'][2]:.2f} m; the modeled roof rises to about 4.75 m. The canopy top is about 5.34 m overall. Evidence labels these heights as estimates and no elevation or measured roof source was found.",
            "Aerial image gives plan/roof silhouette context but does not establish vertical dimensions or exact roof pitch.",
        ],
        "findings": "One-story massing and a low-pitched roof are supported qualitatively. Eave, ridge, canopy elevations, and roof pitch are unverified estimates, so this criterion is only partially awarded.",
    },
    {
        "name": "Facade, entrances, and distinctive architecture",
        "score": 1.75,
        "max_score": 2.0,
        "evidence": [
            "The retained exact-address storefront gallery shows beige wall panels, a broad red Circle K fascia, white trim, a long dark glazed storefront, a front entry, and a red square brand sign; these features appear in the saved render.",
            "Station gallery and aerial evidence also show a freestanding Mobil canopy with blue-and-white fascia and pump islands; the model includes this separate canopy and three islands/six dispenser masses.",
            "Facade bay spacing, sign geometry, pump count/spacing, and canopy structural details are simplified proxies. Photo dates and detailed elevations are unavailable.",
        ],
        "findings": "The distinguishing station and store character is captured with source-backed broad features. Fine fenestration, logo geometry, and accessory details remain approximate for massing.",
    },
    {
        "name": "Modular export, portability, and complete evidence",
        "score": 1.5,
        "max_score": 2.0,
        "evidence": [
            f"Blender {probe['blender_version']} reopened the saved file and found expected scene {probe['scene']} and direct child collection {probe['collection']} with {probe['collection_object_count']} objects ({probe['object_types']}). All evaluated geometry is nonempty; the collection contains no modifiers, linked libraries, or unpacked image dependencies.",
            "Evidence folder contains raw OSM, Indiana footprint query and metadata, imagery tiles/mosaic, exact-address photo snapshots, a permit PDF, previews, reopen validation, source provenance, and explicit uncertainty notes.",
            f"Shared manifest currently declares object_count={probe['manifest_expected_object_count']} and objects={probe['manifest_expected_object_names']}, whereas the reopened collection has {probe['collection_object_count']} objects. This is a real manifest/object-contract discrepancy for coordinator review; the grader did not edit shared files.",
        ],
        "findings": "The .blend library itself reopens cleanly and is portable with well-documented evidence. The shared manifest's expected object count/name list must be reconciled by the coordinator before considering the metadata contract fully clean.",
    },
]

score = round(sum(c["score"] for c in criteria), 2)
result = {
    "building_id": "massing_circle_k_fa39c23",
    "building_name": "Circle K / Mobil, 706 Northwestern Avenue",
    "score": score,
    "max_score": 10,
    "pass_threshold": 8,
    "passed": score >= 8,
    "criteria": criteria,
    "evidence": {
        "asset": probe["asset_path"],
        "asset_sha256": probe["asset_sha256"],
        "blender_version": probe["blender_version"],
        "osm_way": probe["source_way_id"],
        "symmetric_hausdorff_xy_error_m": probe["symmetric_hausdorff_xy_error_m"],
        "store_shell_dimensions_m": probe["store_shell_dimensions_m"],
        "actual_collection_object_count": probe["collection_object_count"],
        "manifest_object_count": probe["manifest_expected_object_count"],
        "external_unpacked_images": probe["external_unpacked_images"],
        "linked_libraries": probe["linked_library_paths"],
        "builder_validation": reopen["result"],
        "evidence_source_count": len(evidence["sources"]),
        "blender_probe": "audit/circle_k_independent_grade/blender_probe.py",
    },
    "findings": [
        "PASS: correct Circle K identity and OSM store polygon; independent vertex comparison error is negligible.",
        "PASS: store position, orientation, and dimensions follow OSM. Separate Mobil canopy is placed south from imagery with dimensions marked approximate.",
        "LIMITATION: floor count and low roof form are supported qualitatively; all vertical dimensions and pitch remain estimates.",
        "PASS WITH MASSING LIMITS: photos support the broad facade and canopy cues; exact facade bay sizing, signage, and pump details are simplified.",
        "COORDINATOR ACTION: manifest says object_count=1 and objects=['Circle K']; current saved collection has 69 objects. Reconcile the shared manifest metadata.",
    ],
    "grade_method": "Scores assess the independent primary-source matches and the reopened geometry. Unsupported vertical measurements are explicitly discounted. Passing threshold is 8/10 as specified by AGENT.md.",
}
OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"score": score, "max_score": 10, "passed": result["passed"], "result": str(OUT)}, indent=2))
