"""Independent TREC grade, based on raw evidence and a direct Blender reopen."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ASSET = ROOT / "modular/buildings/massing_turf_recreation_exercise_center_9622f45.blend"


def evaluate():
    evidence = json.loads((HERE / "evidence.json").read_text(encoding="utf-8"))
    imagery = json.loads((HERE / "footprint_imagery_comparison.json").read_text(encoding="utf-8"))
    reopened = json.loads((HERE / "reopen_validation.json").read_text(encoding="utf-8"))
    gis = json.loads((HERE / "sources/purdue_gis_trec_oid312_2026-10-26.geojson").read_text(encoding="utf-8-sig"))
    osm = json.loads((HERE / "sources/osm_trec_way_283275002_2026-10-26.json").read_text(encoding="utf-8-sig"))
    props = gis["features"][0]["properties"]
    footprint = evidence["measured_geometry"]
    bounds = reopened["world_bounds_m"]
    gis_bounds = footprint["bounds_m"]
    position_conflict = imagery["registration"]["gis_minus_osm_center_m"]

    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "score": 1.6, "max_score": 2,
            "status": "identity and selected Purdue polygon verified; perimeter conflict remains",
            "evidence": [
                f"Raw Purdue GIS feature OBJECTID={props['OBJECTID']} is {props['Name']} (ABBR={props['ABBR']}); raw OSM way {next(e['id'] for e in osm['elements'] if e['type']=='way')} is independently named Turf Recreation Exercise Center.",
                f"The saved wall footprint uses all {footprint['source_vertex_count']} vertices from the Purdue feature and its computed ring area is {footprint['gis_ring_plan_area_m2_computed']:.1f} m2.",
                "The orthophoto shows both Purdue GIS and OSM outlines over the same TREC roof. OSM tracks the visible roof edge more closely in places; neither source establishes the actual structural-wall perimeter.",
                "Purdue area attribute (36,210 sq ft), computed polygon area (~34,124 sq ft), Treasurer list (36,545.51 sq ft), and RecWell project figure (29,037 sq ft) do not reconcile."
            ],
            "findings": ["Keep the roof-edge versus wall-footprint discrepancy explicit; current named Purdue GIS footprint is a defensible source choice, but it is not confirmed as the wall line."]
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "score": 1.3, "max_score": 2,
            "status": "GIS position and north-south axis represented; 2.4 m source conflict unresolved",
            "evidence": [
                f"Reopened asset bounds are X {bounds[0][0]:.3f}..{bounds[0][1]:.3f} m, Y {bounds[1][0]:.3f}..{bounds[1][1]:.3f} m; model dimensions are about {footprint['footprint_bounds_m']['east_west']:.2f} x {footprint['footprint_bounds_m']['north_south']:.2f} m.",
                "The modeled perimeter follows the selected Purdue GIS ring; orthophoto and both GIS/OSM outlines show a long north-south hall, matching the model ridge direction.",
                f"The selected GIS center is {position_conflict[0]:.2f} m west and {abs(position_conflict[1]):.2f} m south of the OSM/prior manifest center; GIS is about 1.21 m narrower east-west. The roof-wall relation is unresolved.",
                "Reopened asset has direct campus-coordinate geometry, as appropriate for this massing asset. Master placement/context is outside this isolated library grade."
            ],
            "findings": ["Coordinator should reconcile the OSM-matching prior manifest bounds against the current Purdue feature and orthophoto before accepting campus placement."]
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "score": 1.5, "max_score": 2,
            "status": "roof silhouette and estimated vertical profile supported; no surveyed elevations or floor count",
            "evidence": [
                "The 2023 orthophoto supports a pale two-plane gable roof, north-south ridge, and repeated east-west transverse roof bands; the reopened model reproduces those broad features.",
                "Raw 2018 Indiana QL2 LiDAR tile analysis reports 7,529 non-ground returns in the OSM roof ring and 12,968 nearby classified-ground returns. Across-width median profile is approximately 9.693/9.665 m at the outer bins and 14.373 m centrally.",
                "Reopened wall envelope is 9.70 m high and roof reaches 14.40 m. Evidence accurately labels these as estimates, not surveyed dimensions; LiDAR has no class-6 building returns in either footprint and uses nearby ground.",
                "No reliable source establishes floor count. The single clear-span hall interpretation is consistent with RecWell use, but this is not proof of story count."
            ],
            "findings": ["Retain estimate labels and uncertainty; no published section/elevation or surveyed eave/ridge height was found."]
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 0.5, "max_score": 2,
            "status": "minimal schematic entry; facade treatment and distinctive features unverified",
            "evidence": [
                "Reopened asset has a neutral, uninterrupted exterior wall envelope and one pair of schematic door panels; render shows no evidence-backed facade rhythm, cladding, glazing, or other distinctive features.",
                "Purdue RecWell accessibility source places a TREC entrance on the circle drive west of CoRec and at grade, supporting the general side/level only. The exact bay, count, dimensions, and materials are not specified.",
                "No TREC-specific exterior elevation or ground-level photo was found in the evidence package. CoRec/AIA imagery is correctly excluded as not TREC-specific."
            ],
            "findings": ["Find a TREC-specific, attributable facade/entrance photo or drawing and model only details it supports. If none exists, keep the facade deliberately neutral and record the unresolved limitation; appearance alone cannot earn these points."]
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 2.0, "max_score": 2,
            "status": "standalone asset and provenance package verified",
            "evidence": [
                f"Direct Blender 4.5 reopen confirms scene {reopened['opened_scene']} and collection {reopened['collection']} with {reopened['object_count']} mesh objects; stable asset path and collection name are preserved.",
                "No file-linked external images are referenced by the reopened library; geometry is directly in campus coordinates for this massing asset.",
                "The folder contains raw Purdue GIS, OSM, RecWell, campus map, 2023 orthophoto, and 2018 LiDAR source snapshots with URLs/providers, IDs, dates, CRS, methods, and uncertainty; four review renders and footprint overlay are present.",
                "Reopen report records evaluated bounds, footprint vertex count, wall/roof heights, and expected collection."
            ],
            "findings": ["No modular export or evidence completeness issue found in the standalone asset. Master integration remains Tobin-owned."]
        }
    ]
    score = round(sum(item["score"] for item in criteria), 2)
    return {
        "building_id": "massing_turf_recreation_exercise_center_9622f45",
        "building_name": "Turf Recreation Exercise Center (TREC)",
        "reviewer": "independent evaluator r3; raw-source, rendered-view, and direct reopened-library inspection",
        "score": score, "max_score": 10, "passing_standard": 8,
        "criteria": criteria,
        "evidence": {
            "directly_reopened_asset": str(ASSET.relative_to(ROOT)),
            "reopen_summary": {k: reopened[k] for k in ("opened_scene", "collection", "object_count", "evaluated_mesh_count", "evaluated_face_count", "world_bounds_m", "gis_perimeter_vertex_count", "wall_z_bounds_m", "roof_z_bounds_m", "material_slots")},
            "source_identity": {"purdue_objectid": props["OBJECTID"], "purdue_name": props["Name"], "purdue_abbr": props["ABBR"], "osm_way_id": next(e["id"] for e in osm["elements"] if e["type"] == "way")},
            "orthophoto_observation": imagery["registration"]["roof_observation"],
            "lidar_analysis": json.loads((HERE / "lidar_height_analysis.json").read_text(encoding="utf-8")),
            "review_renders": ["preview.png", "preview_top.png", "preview_north_gable.png", "preview_east_entry.png", "orthophoto_footprint_overlay.png"]
        },
        "findings": [f for item in criteria for f in item["findings"]],
        "recommendation": "Below 8/10. The model is a defensible evidence-led massing candidate, but source conflict over the wall/roof outline and the unsupported facade/entrance detail limit the grade. Resolve placement with the coordinator and seek attributable TREC-specific exterior evidence; do not invent architectural details if none is available."
    }


if __name__ == "__main__":
    result = evaluate()
    (HERE / "independent_grade_r3.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
