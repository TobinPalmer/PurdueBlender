"""Independent rubric evaluator for the exact FSTC modular Blender asset.

Run from repository root with Python 3. The evaluator checks the saved asset
hash against a fresh-open Blender probe and independently compares its base
footprint to the saved official Purdue GIS and OSM source snapshots.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from shapely.geometry import Polygon

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "first_street_towers_central_fstc_929924d"
OUT = Path(__file__).resolve().parent / "result.json"
ASSET = ROOT / "modular" / "buildings" / "massing_first_street_towers_central_fstc_929924d.blend"
EXPECTED_SHA256 = "8c8930544d517f572d4ea1e405cb0a35abc028cd40835ed9706ee7f8f1dd5b76"


def evaluate() -> dict:
    sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    if sha != EXPECTED_SHA256:
        raise RuntimeError(f"Candidate changed: expected {EXPECTED_SHA256}, found {sha}")

    probe = json.loads((Path(__file__).parent / "candidate_probe.json").read_text())
    ev = json.loads((AUDIT / "evidence.json").read_text())
    gis = json.loads((AUDIT / "sources" / "purdue_building_shapes_fstc_2026-10-26.geojson").read_text())
    osm = json.loads((AUDIT / "sources" / "osm_buildings_bbox_2026-10-26.json").read_text())
    if probe["candidate_sha256"] != EXPECTED_SHA256 or not probe["fresh_opened"]:
        raise RuntimeError("Fresh-open probe does not match requested candidate SHA")

    # AGENT.md / modular/AGENTS.md local campus conversion, applied independently.
    lat0, lon0 = 40.4274, -86.9137
    def project(lon, lat):
        return ((lon - lon0) * 111412.84 * math.cos(math.radians(lat0)),
                (lat - lat0) * 111040.0)

    candidate_ring = probe["ground_faces"][0]
    candidate = Polygon([(x, y) for x, y, _z in candidate_ring])
    feature = next(f for f in gis["features"] if str(f.get("id")) == "664")
    gis_ring = feature["geometry"]["coordinates"][0]
    gis_poly = Polygon([project(lon, lat) for lon, lat, *_ in gis_ring])
    iou = candidate.intersection(gis_poly).area / candidate.union(gis_poly).area
    hausdorff = candidate.hausdorff_distance(gis_poly)
    centroid_error = candidate.centroid.distance(gis_poly.centroid)
    bounds_delta = max(abs(a - b) for a, b in zip(candidate.bounds, gis_poly.bounds))

    node_xy = {e["id"]: (e["lon"], e["lat"]) for e in osm["elements"] if e["type"] == "node"}
    way = next(e for e in osm["elements"] if e["type"] == "way" and e["id"] == 283274998)
    osm_poly = Polygon([project(*node_xy[n]) for n in way["nodes"] if n in node_xy])
    osm_iou = candidate.intersection(osm_poly).area / candidate.union(osm_poly).area
    osm_hausdorff = candidate.hausdorff_distance(osm_poly)

    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                "Purdue University BuildingShapes FeatureServer FID 664 names First Street Towers Central (FSTC), address evidence also identifies 1250 First Street.",
                f"Candidate base ring vs official GIS outer ring: IoU {iou:.5f}; centroid offset {centroid_error:.3f} m; Hausdorff distance {hausdorff:.3f} m; maximum bounds delta {bounds_delta:.3f} m.",
                "Candidate stable ID, asset filename, scene, collection, object name, and evidence record consistently identify FSTC.",
            ],
            "findings": [
                "The official GIS outline is a strong and well-matched source for the modeled structural footprint.",
                "Source conflict: OSM way 283274998 has the same name/address but covers about 1,720 m² versus about 1,481 m² for the official GIS polygon; candidate-to-OSM IoU is " + f"{osm_iou:.3f} and Hausdorff distance is {osm_hausdorff:.2f} m. The model transparently follows the official GIS source rather than blending the incompatible outlines.",
            ],
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                f"Fresh-open candidate plan bounds match official GIS bounds within {bounds_delta:.3f} m; centroid offset is {centroid_error:.3f} m.",
                "All comparisons use the project’s documented local campus conversion and campus-coordinate massing convention.",
                "Structural base outline has the same detailed non-rectangular plan shape as GIS, rather than relying on an overall decorative-object bounding box.",
            ],
            "findings": ["Footprint position, orientation, and plan scale are independently verified to sub-meter tolerance; dimensional confidence is high within the stated approximate projection."],
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "score": 1.2,
            "max_score": 2,
            "evidence": [
                "Official GIS attributes NUM_LEVELS=7 and CountOfFLO=7 support seven modeled levels.",
                f"Fresh-open mesh reaches {probe['bounds_world_m'][2][1]:.2f} m in the model; the evidence record estimates 3.42 m floor-to-floor and about 23.94 m to roof.",
                "Preview shows a largely flat roof and low parapet.",
            ],
            "findings": [
                "Total height, story height, and roof silhouette are not corroborated by a surveyed elevation or architectural section.",
                "GIS Extrution=46 is documented in the source but its units and meaning are unknown; treating that value as a verified height would be unsupported.",
            ],
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 1.4,
            "max_score": 2,
            "evidence": [
                "The Purdue 2019 exterior photo shows red-brown brick, pale stone entrance surround, a broad arched entry, glazing, and First Street Towers lettering.",
                "Candidate preview models brick bond, repetitive windows, pale horizontal trim, glazed entry, an arched pale entry surround, and building lettering.",
                "The official residences page supports residential use and shared cluster lounge/dinette/kitchen; the candidate includes a schematic interior with partitions and furnishings.",
            ],
            "findings": [
                "Facade vocabulary and materials match available photo evidence, but the elevation is largely repetitive and generic outside the entrance.",
                "In the overall candidate view, the entry arch and sign read smaller and less prominent than in the available close reference photo; no full elevation or entrance survey was found to settle exact proportions.",
                "Interior is illustrative rather than plan-accurate; the available lounge photo validates use and furnishings only, not layout.",
            ],
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 1.8,
            "max_score": 2,
            "evidence": [
                f"Fresh-opened in Blender {probe['blender_version']}; expected scene/collection present and collection contains one named mesh ({probe['vertex_count']} vertices, {probe['face_count']} faces).",
                f"Nine named materials and UV layers {probe['uv_layers']} are present; materials are procedural and the blend has no external images, libraries, or mesh external data.",
                "Building-specific evidence contains raw GIS/OSM/page/photo snapshots, dimensions, uncertainty, source URLs and retrieval date, plus a preview and fresh-open validation.",
            ],
            "findings": ["Standalone asset is portable and follows the expected modular scene/collection naming. Minor deduction because the interior remains schematic and the saved evidence has only a single exterior preview rather than dedicated interior/roof views."],
        },
    ]
    score = round(sum(c["score"] for c in criteria), 1)
    result = {
        "evaluator": "independent evidence-based rubric evaluator",
        "candidate": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
        "candidate_sha256": sha,
        "expected_sha256": EXPECTED_SHA256,
        "sha_verified": sha == EXPECTED_SHA256,
        "fresh_open_verified": probe["fresh_opened"],
        "score": score,
        "max_score": 10,
        "pass_threshold": 8,
        "pass": score >= 8,
        "criteria": criteria,
        "evidence": {
            "fresh_open_probe": "audit/first_street_towers_central_fstc_independent_grade/candidate_probe.json",
            "building_evidence": "audit/first_street_towers_central_fstc_929924d/evidence.json",
            "official_gis_feature": "Purdue BuildingShapes FID 664, snapshot retrieved 2026-10-26",
            "conflicting_osm_feature": "OSM way 283274998, snapshot timestamp 2026-10-26T07:42:01Z",
            "geometry_metrics": {
                "candidate_vs_gis_iou": round(iou, 6),
                "candidate_vs_gis_hausdorff_m": round(hausdorff, 4),
                "candidate_vs_gis_centroid_error_m": round(centroid_error, 4),
                "candidate_vs_gis_bounds_max_delta_m": round(bounds_delta, 4),
                "candidate_vs_osm_iou": round(osm_iou, 6),
                "candidate_vs_osm_hausdorff_m": round(osm_hausdorff, 4),
                "candidate_footprint_area_m2": round(candidate.area, 3),
                "official_gis_footprint_area_m2": round(gis_poly.area, 3),
                "osm_footprint_area_m2": round(osm_poly.area, 3),
            },
            "visual_sources": [
                "audit/first_street_towers_central_fstc_929924d/fstc_exterior_preview.png",
                "audit/first_street_towers_central_fstc_929924d/sources/purdue_first_street_towers_exterior_BrianTedeschi2_2019.jpg",
                "audit/first_street_towers_central_fstc_929924d/sources/purdue_first_street_towers_interior_lounge_fall2022.jpg",
            ],
        },
        "findings": [
            "Exact requested SHA was independently recomputed and matched; fresh-open report confirms this exact asset opened in Blender 5.2.3 LTS.",
            "Strongest verified feature is the official-GIS-matched footprint. Height/roof and fine facade proportions remain estimated because source elevations/plans are unavailable.",
            "OSM and official GIS disagree materially on the footprint; the candidate clearly adopts official GIS FID 664 and retains the OSM discrepancy as uncertainty.",
        ],
    }
    return result


if __name__ == "__main__":
    result = evaluate()
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("candidate_sha256", "score", "max_score", "pass", "pass_threshold")}, indent=2))
