"""Independent r3 rubric evaluator for Jimmy John's.

Scores only source-supported claims and recorded validation. Run from anywhere:
    python audit/massing_jimmy_john_s_12edba1/independent_grade/r3/evaluate_jimmy_johns.py
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[4]
AUDIT = ROOT / "audit" / "massing_jimmy_john_s_12edba1"


def evaluate():
    evidence = json.loads((AUDIT / "evidence.json").read_text(encoding="utf-8"))
    validation = json.loads((AUDIT / "direct_validation.json").read_text(encoding="utf-8"))
    refs = json.loads((AUDIT / "sources" / "reference_index.json").read_text(encoding="utf-8"))
    state = validation["independent_footprint_crosscheck"]
    preview = AUDIT / "renders" / "jimmy_johns_facade_preview.png"
    overlay = AUDIT / "renders" / "footprint_overlay_indiana_2018_detail.png"
    ortho = AUDIT / "renders" / "indiana_2018_ortho.png"

    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 1.75,
            "max_score": 2,
            "evidence": [
                "The official Jimmy John's directory and OSM way 116427223 independently match the 311 W State St address/store identity.",
                "IndianaMap's statewide 2016-2020 LiDAR-derived feature objectid 443017 (Tippecanoe, lidar year 2018) is the selected primary ring; its raw WGS84 polygon is saved and the dated 2018 ortho overlay was inspected.",
                "The model preserves the state ring rather than averaging it with OSM. The overlay shows both rings at the same roof, with the OSM outline mostly inset and the state ring extending beyond visible roof edges in some places.",
                "Ground-projected state area is 258.65 m² / 2,784 sq ft; raw SHAPE__Area is correctly distinguished as Web Mercator. County imagery accuracy is reported as ±2.5 ft at 90%, not a feature-specific confidence interval.",
            ],
            "finding": "Identity and the choice of a dated exterior outline are well supported. The exact wall-versus-roof boundary remains ambiguous at the imagery's alignment/accuracy scale, so the polygon is not a surveyed wall footprint.",
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 1.5,
            "max_score": 2,
            "evidence": [
                "The state polygon is projected from its saved WGS84 coordinates using the repository's documented local campus approximation; its orientation is preserved in campus XY.",
                "The saved reopen validation records identity object transform and every primary footprint corner at ground within 1 mm. Primary-ring bounds are about 16.85 × 21.03 m.",
                "The OSM ring centroid is 0.706 m away and serves as a location corroboration only. Model envelope extends roughly 0.46 m and 0.58 m beyond the primary ring from schematic roof/eave geometry.",
                "No surveyed coordinate or dimension source is available; state-image horizontal accuracy and roof-edge-versus-wall interpretation limit absolute positional and scale claims.",
            ],
            "finding": "The asset faithfully retains its selected geospatial outline and nearby site location. Absolute position and wall dimensions are not independently surveyed, and the geometric outline may describe the roof rather than the wall line.",
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 1.25,
            "max_score": 2,
            "evidence": [
                "The historical storefront photo visibly supports one story, a broad shallow roof, and deep eaves; the official 2017 BZA-1963 minutes refer to an existing building and a new roof.",
                "The modeled 4.0–5.0 m edge heights, 1.0 m rise, slope direction, and roughly 0.46–0.58 m eaves are explicitly marked as visual estimates. No elevation, measured roof profile, or original plan is present.",
                "The saved preview shows a low single-plane roof, but its camera view cannot verify numerical height or pitch.",
            ],
            "finding": "Broad story count and roof silhouette are evidenced; numeric height, slope, direction, and eave dimensions remain unmeasured visual proportions.",
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1.5,
            "max_score": 2,
            "evidence": [
                "The historical image supports continuous glazed storefronts, light mullions, a projecting circular sign, and deep eaves; these cues are visible in the inspected preview.",
                "BZA-1963 records site renovation with new glass, a new roof and patio, and an allowed 36-inch sign (the requested 54-inch sign was denied). This supports the renovation/sign context, not precise facade geometry.",
                "The photo's date is unknown. Its approximate 15–17 narrow long-side bays and 4–6 return sections are perspective-limited; door position, exact bay spacing, and current appearance remain schematic or unverified.",
            ],
            "finding": "Distinctive storefront and sign cues are represented and have historical-photo support, with some renovation context from county minutes. Exact entrance/facade layout and current tenant appearance are not verified.",
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                f"The saved direct-reopen record names the expected scene and collection and confirms {validation['mesh_object_count']} mesh object, {validation['vertex_count']} vertices, {validation['polygon_count']} polygons, and {validation['modifier_count']} modifiers.",
                "The reopen record reports identity transforms, no linked libraries, no external image paths, and exact primary-ring ground vertices; the asset path and collection identifiers match the evidence record.",
                "The evidence package contains raw state and OSM snapshots, source index, official store snapshot, historical/property notes, 2018 imagery and overlays, facade preview, builder script, and direct validation.",
                "The model is authored as one simple campus-coordinate massing asset, with camera kept outside the exported collection.",
            ],
            "finding": "Recorded export, portability, reopen checks, and inspectable evidence package are complete. This grading pass could not independently reopen the binary because the live Blender connection and local Blender executable were unavailable.",
        },
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    return {
        "asset_id": "massing_jimmy_john_s_12edba1",
        "building": "Jimmy John's",
        "review_type": "independent rubric review r3",
        "score": score,
        "max_score": 10,
        "passing_threshold": 8,
        "passed": score >= 8,
        "criteria": criteria,
        "evidence": {
            "files_inspected": [
                "modular/buildings/massing_jimmy_john_s_12edba1.blend (existence/path; geometry reviewed through saved Blender reopen record)",
                "modular/buildings/build_massing_jimmy_john_s_12edba1.py",
                "modular/manifest.json",
                "audit/massing_jimmy_john_s_12edba1/evidence.json",
                "audit/massing_jimmy_john_s_12edba1/direct_validation.json",
                "audit/massing_jimmy_john_s_12edba1/sources/reference_index.json",
                "audit/massing_jimmy_john_s_12edba1/sources/indiana_lidar_footprint_2016_2020.json",
                "audit/massing_jimmy_john_s_12edba1/sources/openstreetmap_way_116427223.json",
                "audit/massing_jimmy_john_s_12edba1/sources/footprint_resolution_r3.txt",
                "audit/massing_jimmy_john_s_12edba1/sources/historical_photo_and_property_notes.txt",
                "audit/massing_jimmy_john_s_12edba1/renders/jimmy_johns_facade_preview.png",
                "audit/massing_jimmy_john_s_12edba1/renders/footprint_overlay_indiana_2018_detail.png",
                "audit/massing_jimmy_john_s_12edba1/renders/indiana_2018_ortho.png",
            ],
            "source_providers": sorted(s["provider"] for s in refs["sources"]),
            "preview_exists": preview.is_file(),
            "inspected_footprint_overlay_exists": overlay.is_file(),
            "dated_ortho_export_exists": ortho.is_file(),
            "saved_reopen_record": validation.get("reopened", False),
            "reopen_mesh_object_count": validation.get("mesh_object_count"),
            "reopen_vertex_count": validation.get("vertex_count"),
            "reopen_polygon_count": validation.get("polygon_count"),
            "reopen_primary_feature_id": state["feature_objectid"],
            "reopen_primary_lidar_year": state["lidar_year"],
            "live_blender_recheck": "unavailable; addon connection failed and no local Blender executable was found",
            "review_limit": "The binary was not reopened in this r3 pass. Geometry and portability scores rely on the saved Blender 4.5.15 direct-reopen record, the build script/source data, and inspected renders.",
        },
        "findings": [
            "Compared with earlier reviews, the primary outline is now the independent dated Indiana 2018 LiDAR-derived feature; its overlay against 2018 ortho and the OSM corroboration were inspected directly.",
            "The selected ring is a defensible exterior massing outline, but its edge may follow roof overhang rather than wall; horizontal residuals and source accuracy do not support a surveyed footprint claim.",
            "Official BZA-1963 minutes strengthen the existing-building, renovation, new-glass/roof, patio, and sign context, while leaving architectural dimensions unprovided.",
            "The broad one-story, shallow-roof and storefront cues are source-backed. Exact height, pitch, eaves, mullion spacing, entrance location, and current facade remain visual estimates or unresolved.",
            "The saved export/reopen validation and structured evidence package are complete; live binary inspection could not be repeated during this review.",
        ],
    }


if __name__ == "__main__":
    result = evaluate()
    out = Path(__file__).with_name("result.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
