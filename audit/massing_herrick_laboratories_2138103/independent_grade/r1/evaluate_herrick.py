"""Independent rubric evaluator for the saved Herrick Acoustics asset.
Run with: python evaluate_herrick.py
Source observations were made by reopening the .blend in Blender and comparing its
geometry and renders with the retained Purdue GIS, history, newsletter, and photo evidence.
"""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
inspection = json.loads((HERE / "direct_inspection.json").read_text(encoding="utf-8"))
source_path = ROOT / "audit/massing_herrick_laboratories_2138103/sources/purdue_building_shapes_fid246_herl_2026-10-26.json"
feature_record = json.loads(source_path.read_text(encoding="utf-8-sig"))["features"][0]
attrs = feature_record["attributes"]
assert inspection["source"]["FID"] == 246
assert inspection["source"]["abbr"] == "HERL"
assert inspection["source"]["name"] == "Herrick Acoustics"
assert inspection["collection"] == "Asset_massing_herrick_laboratories_2138103"
assert inspection["scene"] == "Building_massing_herrick_laboratories_2138103"
assert inspection["collection_object_count"] == 1
assert inspection["modifiers"] == []

criteria = [
    {
        "criterion": "Correct identity and source-backed footprint",
        "score": 2.0, "max_score": 2,
        "assessment": "Pass. The opened asset is labeled Herrick Acoustics; its wall base matches the 66-vertex transformed GIS FID 246 / HERL ring to a maximum nearest-vertex difference of 0.000037 m. Purdue's facilities/history sources identify the original 1920s horse barn and explicitly distinguish it from the 2013 new Herrick building, avoiding confusion with FID 878 / HLAB.",
        "uncertainty": "The GIS polygon is not a surveyed structural-wall survey, and its Shape__Area attribute conflicts with the area computed from the returned ring. The polygon identity and vertex agreement remain direct evidence."
    },
    {
        "criterion": "Position, orientation, and scale/dimensions",
        "score": 1.8, "max_score": 2,
        "assessment": "The reopened mesh is in campus coordinates and the bottom outline overlays the GIS ring under the documented local approximation. Its total bounds are 78.547 x 84.019 m, including facade projections; the GIS wall ring itself is the stronger plan evidence. No separate survey or measured dimensions are retained.",
        "uncertainty": "The local geographic conversion is approximate, and the transformed ring area (2993.81 m²) differs from GIS Shape__Area (5174.79 m²); the footprint ring, rather than the area attribute, is modeled."
    },
    {
        "criterion": "Evidence-backed height, floors, and roof form",
        "score": 1.1, "max_score": 2,
        "assessment": "The GIS record reports three levels and Extrution=36. Historical imagery supports the central barn's pitched roof, cupola, and dormers, and the newer photo supports lower flanking wings. The mesh is 10.95 m high with 5.2 m wing height.",
        "uncertainty": "No elevation or measured height source supports 10.95 m or 5.2 m. The 36-unit field has undocumented units and is interpreted as feet; the three-level field does not validate the varied wing/barn heights. Exact roof geometry is photo-derived."
    },
    {
        "criterion": "Facade, entrances, and distinctive architecture",
        "score": 1.0, "max_score": 2,
        "assessment": "The asset includes red-brown brick, broad low wings around a courtyard, central raised barn volume, red roof, cupola, dormers, window elements, and a courtyard entrance/canopy. These motifs are visible in the 2009 institutional newsletter images and the retained Lab Manager photo of the original building.",
        "uncertainty": "The saved courtyard render simplifies the photographic facade: window bands and entrance composition are sparse, while the original photo shows more continuous glazing, visible wall piers, and a more legible roof-to-wall profile. Facade stationing and entrance position are not measured."
    },
    {
        "criterion": "Modular export, portability, and complete evidence",
        "score": 2.0, "max_score": 2,
        "assessment": "The saved file reopens with the expected named scene and collection, one mesh object, no modifiers, local material data, and no external file-image dependencies. Dedicated source snapshots/catalog, validation record, and two renders are present.",
        "uncertainty": "The library is a self-contained campus-coordinate asset; any future collection-instance use should retain the project placement convention."
    }
]
score = round(sum(c["score"] for c in criteria), 1)
result = {
    "building_id": "massing_herrick_laboratories_2138103",
    "review_revision": "r1",
    "score": score,
    "max_score": 10,
    "passing_threshold": 8,
    "passed": score >= 8,
    "criteria": criteria,
    "evidence": {
        "asset": "modular/buildings/massing_herrick_laboratories_2138103.blend",
        "direct_reopen_measurements": "audit/massing_herrick_laboratories_2138103/independent_grade/r1/direct_inspection.json",
        "gis_feature": "audit/massing_herrick_laboratories_2138103/sources/purdue_building_shapes_fid246_herl_2026-10-26.json",
        "institutional_history_and_facilities": ["audit/massing_herrick_laboratories_2138103/sources/purdue_herrick_history_2026-10-26.html", "audit/massing_herrick_laboratories_2138103/sources/purdue_herrick_facilities_2026-10-26.html"],
        "historic_visual_sources": ["audit/massing_herrick_laboratories_2138103/sources/herrick_laboratories_newsletter_spring_2009.pdf", "audit/massing_herrick_laboratories_2138103/sources/herrick_labs_original_photo_labmanager.jpg"],
        "review_renders": ["audit/massing_herrick_laboratories_2138103/renders/herrick_acoustics_courtyard_preview.png", "audit/massing_herrick_laboratories_2138103/renders/herrick_acoustics_plan_preview.png"],
        "direct_measurements": inspection,
        "source_attributes": {"FID": attrs.get("FID"), "BUILDING_N": attrs.get("BUILDING_N"), "BLDG_ABBR": attrs.get("BLDG_ABBR"), "NUM_LEVELS": attrs.get("NUM_LEVELS"), "Extrution": attrs.get("Extrution"), "Shape__Area": attrs.get("Shape__Area")}
    },
    "findings": [
        {"severity": "major", "finding": "Height and wing elevations are estimates: the GIS Extrution=36 units are not documented, and the evidence set has no measured elevation. The model's feet interpretation and 5.2 m wings remain unverified.", "action": "Seek a dimensioned elevation, as-built plan, or authoritative building height record; otherwise keep these values explicitly labeled as estimates."},
        {"severity": "moderate", "finding": "The courtyard render conveys the correct broad composition but underrepresents the source photo's continuous wing window bands, wall piers, and central entrance/roof-to-wall articulation.", "action": "Use the retained historic/current photographs to revise or document the facade/window rhythm and entrance placement, then render a comparable courtyard elevation."},
        {"severity": "moderate", "finding": "The GIS Shape__Area value (5174.79 m²) is substantially larger than the approximate transformed ring area (2993.81 m²). The shell follows the returned FID 246 geometry directly, but the attribute conflict is unexplained.", "action": "Check the layer's native area computation and polygon topology/units; preserve the source ring as the footprint unless authoritative geometry shows otherwise."}
    ]
}
(HERE / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({"score": score, "max_score": 10, "passed": result["passed"], "criteria": [{"criterion": c["criterion"], "score": c["score"], "max_score": c["max_score"]} for c in criteria], "findings": result["findings"]}, indent=2))
