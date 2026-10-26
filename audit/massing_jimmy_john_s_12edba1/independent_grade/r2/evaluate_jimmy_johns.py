"""Independent r2 rubric evaluation for the Jimmy John's library asset."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[4]
AUDIT = ROOT / "audit" / "massing_jimmy_john_s_12edba1"


def evaluate():
    evidence = json.loads((AUDIT / "evidence.json").read_text(encoding="utf-8"))
    validation = json.loads((AUDIT / "direct_validation.json").read_text(encoding="utf-8"))
    refs = json.loads((AUDIT / "sources" / "reference_index.json").read_text(encoding="utf-8"))
    state = validation["independent_footprint_crosscheck"]
    scores = [1.5, 1.5, 1.0, 1.5, 2.0]
    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": scores[0], "max_score": 2,
            "evidence": [
                "Official Jimmy John's directory and OSM way 116427223 independently identify 311 W State St / store 9006.",
                "IndianaMap's independent 2018 LiDAR-derived objectid 443017 overlaps this site, adding a second footprint source beyond OSM.",
                "The Indiana ground-area estimate (~2,784 sq ft), OSM ring (~2,252 sq ft), and LoopNet property figure (1,908 sq ft) differ; no source establishes the exact current wall boundary.",
            ],
            "finding": "Identity is strongly supported and the state LiDAR polygon corroborates a footprint at the site, but its roughly 24% larger area than OSM and differing LoopNet basis leave exact footprint geometry unresolved.",
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": scores[1], "max_score": 2,
            "evidence": [
                "The rebuilt asset retains the OSM structural ring at ground level within 1 mm and has identity object transform.",
                "The state polygon centroid lies at the same site and its rectangular orientation is similar; its bounds are larger, so it supports placement more than exact dimensions.",
                "No surveyed campus position, orientation, or building dimensions are available; the footprint-area conflict remains material.",
            ],
            "finding": "OSM coordinates, orientation, and dimensions are reproducibly retained, and the independent state polygon supports the location. Exact position and plan dimensions lack survey confirmation and cross-source dimensions conflict.",
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": scores[2], "max_score": 2,
            "evidence": [
                "The saved historical photo supports a one-story building, shallow roof silhouette, and deep eaves.",
                "The 4–5 m roof-edge range, mono-plane selection, 1 m rise (~3.9 degrees), slope direction, and 0.5–0.63 m eaves are explicitly estimates; no measured elevation or roof drawing is cited.",
            ],
            "finding": "The broad story count and roof appearance are photo-supported, but nearly all numeric vertical and roof geometry is estimated from an undated image.",
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": scores[3], "max_score": 2,
            "evidence": [
                "The historical photo supports long glazing, light mullions, and a round projecting corner sign; these cues appear in the preview.",
                "The entrance location and storefront bay dimensions are schematic, and current facade changes are unverified.",
            ],
            "finding": "Distinctive historical facade cues are represented, while door placement, bay rhythm, and present-day appearance remain uncertain.",
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": scores[4], "max_score": 2,
            "evidence": [
                f"Saved direct-reopen record confirms the expected scene and collection, {validation['mesh_object_count']} mesh, {validation['vertex_count']} vertices, and {validation['polygon_count']} polygons.",
                "The asset has identity transforms, no modifiers, no external libraries or external image paths, and a saved preview.",
                "Structured source snapshots, evidence, direct validation, and source uncertainty are present; the simple massing asset remains in campus coordinates.",
            ],
            "finding": "The modular library and portability checks are recorded as complete, with a source and validation package sufficient to inspect the remaining uncertainties.",
        },
    ]
    score = sum(c["score"] for c in criteria)
    return {
        "asset_id": "massing_jimmy_john_s_12edba1",
        "building": "Jimmy John's",
        "review_type": "independent rubric review r2",
        "score": score, "max_score": 10, "passing_threshold": 8,
        "passed": score >= 8,
        "criteria": criteria,
        "evidence": {
            "files_inspected": [
                "modular/buildings/massing_jimmy_john_s_12edba1.blend (saved-asset properties via direct_validation.json)",
                "modular/buildings/build_massing_jimmy_john_s_12edba1.py",
                "modular/manifest.json",
                "audit/massing_jimmy_john_s_12edba1/evidence.json",
                "audit/massing_jimmy_john_s_12edba1/direct_validation.json",
                "audit/massing_jimmy_john_s_12edba1/sources/reference_index.json",
                "audit/massing_jimmy_john_s_12edba1/sources/openstreetmap_way_116427223.json",
                "audit/massing_jimmy_john_s_12edba1/sources/indiana_lidar_footprint_2016_2020.json",
                "audit/massing_jimmy_john_s_12edba1/sources/historical_photo_and_property_notes.txt",
                "audit/massing_jimmy_john_s_12edba1/renders/jimmy_johns_facade_preview.png",
            ],
            "source_providers": sorted(s["provider"] for s in refs["sources"]),
            "preview_exists": (AUDIT / "renders" / "jimmy_johns_facade_preview.png").is_file(),
            "saved_reopen_record": validation.get("reopened", False),
            "independent_state_footprint_feature": state["feature_objectid"],
            "state_lidar_derived_ground_area_sqft": state["ground_area_sqft"],
            "state_shape_area_web_mercator_m2": state["reported_shape_area_web_mercator_m2"],
            "osm_ground_area_sqft": evidence["model_summary"]["structural_footprint_area_sqft"],
            "review_limit": "The Blender executable/live session was unavailable to this grader. I independently inspected the saved asset's structured reopen measurements and preview; geometry values are attributed to that saved direct-validation record.",
        },
        "findings": [
            "The official directory verifies the current business address; the historical photo and map link add architectural and site context.",
            "The Indiana 2018 LiDAR-derived polygon materially improves source triangulation for footprint/site identity, but it does not resolve the boundary because its area differs from OSM and property floor area.",
            "The model exactly carries forward the selected OSM wall ring and campus location; no independent surveyed coordinate or dimension source is available.",
            "Only story count and broad roof silhouette are photo-supported; modeled heights, roof plane geometry, and precise facade layout remain estimates.",
            "The expected portable collection, saved reopen record, preview, and source snapshots are complete.",
        ],
    }


if __name__ == "__main__":
    result = evaluate()
    out = Path(__file__).with_name("result.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
