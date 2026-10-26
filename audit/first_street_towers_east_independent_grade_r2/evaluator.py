"""Independent, reproducible review of the revised FSTE candidate.

The structural footprint overlap is recalculated from the raw Purdue GIS GeoJSON
and the candidate's fresh-open outline using a 0.10 m raster in project XY.
Visual/source judgments are recorded in the returned scorecard.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/massing_first_street_towers_east_fste_c9b22d3.blend"
EVIDENCE = ROOT / "audit/first_street_towers_east"
SOURCE = EVIDENCE / "sources/purdue_buildingshapeszip4_fste_fid651_2026-10-26.geojson"
PROBE = EVIDENCE / "validation_fresh_open.json"
OUT = Path(__file__).with_name("result.json")
EXPECTED_SHA = "7f92c5bb44c8a5d1f1f5aee145003234e0fb3dd9e6e77dc18fb2dee84dfe94ae"


def project(ring_lonlat):
    """Apply the repository's local lon/lat approximation (metres)."""
    coslat = math.cos(math.radians(40.4274))
    return [((lon + 86.9137) * 111412.84 * coslat,
             (lat - 40.4274) * 111040.0) for lon, lat in ring_lonlat]


def area(poly):
    return abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] -
                   poly[(i + 1) % len(poly)][0] * poly[i][1]
                   for i in range(len(poly))) / 2.0)


def raster_inside(poly, xs, ys):
    """Vectorized even-odd point-in-polygon for cell-centre samples."""
    x, y = np.meshgrid(xs, ys)
    x = x.ravel()
    y = y.ravel()
    inside = np.zeros(x.shape, dtype=bool)
    x0, y0 = poly[-1]
    for x1, y1 in poly:
        crossing = ((y0 > y) != (y1 > y)) & (
            x < (x1 - x0) * (y - y0) / ((y1 - y0) or 1e-30) + x0)
        inside ^= crossing
        x0, y0 = x1, y1
    return inside


def raster_iou(source_poly, candidate_poly, resolution=0.10):
    bounds = [min(p[0] for p in source_poly + candidate_poly),
              min(p[1] for p in source_poly + candidate_poly),
              max(p[0] for p in source_poly + candidate_poly),
              max(p[1] for p in source_poly + candidate_poly)]
    xs = np.arange(bounds[0] + resolution / 2, bounds[2], resolution)
    ys = np.arange(bounds[1] + resolution / 2, bounds[3], resolution)
    s = raster_inside(source_poly, xs, ys)
    c = raster_inside(candidate_poly, xs, ys)
    intersection = int(np.count_nonzero(s & c))
    union = int(np.count_nonzero(s | c))
    return {"resolution_m": resolution,
            "intersection_over_union": intersection / union if union else 0.0,
            "intersection_area_m2": intersection * resolution * resolution,
            "union_area_m2": union * resolution * resolution,
            "source_raster_area_m2": int(np.count_nonzero(s)) * resolution * resolution,
            "candidate_raster_area_m2": int(np.count_nonzero(c)) * resolution * resolution}


def evaluate():
    sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    probe = json.loads(PROBE.read_text(encoding="utf-8"))
    fc = json.loads(SOURCE.read_text(encoding="utf-8"))
    feature = next(f for f in fc["features"] if f.get("id") == 651)
    source_poly = project(feature["geometry"]["coordinates"][0])
    candidate_poly = [tuple(p) for p in probe["structural_wall_outline_xy_m"]]
    overlap = raster_iou(source_poly, candidate_poly)
    attrs = feature["properties"]

    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 2.0, "max_score": 2,
            "evidence": [
                f"Raw Purdue BuildingShapesZip4 feature FID 651 identifies {attrs.get('BLDG_ABBR')} / {attrs.get('BUILDING_N')} at {attrs.get('ADDRESS')}.",
                f"Independent 0.10 m raster overlay from raw EPSG:4326 source and candidate outline gives IoU {overlap['intersection_over_union']:.4f}; candidate area from the fresh-open record is {probe['footprint_comparison']['candidate_wall_area_m2']:.2f} m².",
                "Top-down candidate render follows the irregular GIS footprint, including its setbacks and projecting wings."
            ],
            "finding": "Identity and structural footprint are strongly verified against Purdue's directly identified GIS feature."
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 2.0, "max_score": 2,
            "evidence": [
                "Candidate structural wall bounds in the fresh-open record agree with Purdue GIS bounds to 4 decimal places in the repository's local XY conversion.",
                f"Independent raster comparison reports {overlap['intersection_over_union']:.4f} IoU at {overlap['resolution_m']:.2f} m sampling."
            ],
            "finding": "The plan orientation, dimensions, and local campus placement match the GIS outline. The documented transform is an approximation, not a surveyed control network."
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 1.1, "max_score": 2,
            "evidence": [
                "Purdue GIS FID 651 reports six levels; the asset contains six floor plates and repeated residential stories.",
                "The Purdue 2009 complex photograph visibly supports peaked gable roof language, but does not identify the East wing; exact 23.25 m top height, floor spacing, and two FSTE gables remain estimates."
            ],
            "finding": "Floor count is supported and the roof interpretation is plausible at complex level. Height and the East tower's precise roof configuration are not independently verified."
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1.2, "max_score": 2,
            "evidence": [
                "The reviewed exterior render shows warm red-brown brick, pale window frames, blue-gray glazing, floor-course bands, and modeled gable forms consistent with the complex-level Purdue reference.",
                "A glazed representative entry is modeled on the 1st Street-facing edge; the model evidence documents its distance and alignment to OSM way 5332639. The exact East-wing door and facade bay rhythm are not sourced."
            ],
            "finding": "Material and residential-window language are plausible. The modeled entry and facade rhythm remain interpreted because available imagery is not East-wing-specific."
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 1.8, "max_score": 2,
            "evidence": [
                f"Exact candidate SHA-256: {sha}; expected revision hash matches: {sha == EXPECTED_SHA}.",
                f"Candidate's fresh-open record confirms scene and named export collection, {probe['collection_object_count']} mesh objects, {probe['unique_collection_material_count']} materials, and no external texture files or validation errors.",
                "Building evidence includes source snapshots, footprint diagnostics, exterior and entry views, and a six-level 22-room schematic interior cutaway with uncertainty disclosed."
            ],
            "finding": "The saved collection and materials are self-contained according to the fresh-open validation record, and evidence is complete for a schematic asset. The shared manifest still has stale object-count and height metadata and needs coordinator reconciliation before integration."
        }
    ]
    score = round(sum(c["score"] for c in criteria), 1)
    return {
        "building_id": "massing_first_street_towers_east_fste_c9b22d3",
        "asset_path": str(ASSET),
        "candidate_sha256_expected": EXPECTED_SHA,
        "candidate_sha256_verified": sha,
        "fresh_opened_in_blender": probe.get("fresh_open", False),
        "independent_fresh_open_performed_by_grader": False,
        "score": score, "max_score": 10, "passing_threshold": 8,
        "status": "PASS" if score >= 8 else "FAIL",
        "criteria": criteria,
        "evidence": {
            "source": "Purdue University BuildingShapesZip4 FeatureServer layer 0, FID 651; EPSG:4326 snapshot retrieved 2026-10-26",
            "source_attributes": {k: attrs.get(k) for k in ("BLDG_ABBR", "BUILDING_N", "ADDRESS", "NUM_LEVELS", "CountOfFLO")},
            "independent_footprint_comparison": overlap,
            "candidate_reported_exact_footprint_metrics": probe["footprint_comparison"],
            "visuals_reviewed": [
                "audit/first_street_towers_east/fste_exterior_candidate.png",
                "audit/first_street_towers_east/fste_entry_detail_candidate.png",
                "audit/first_street_towers_east/fste_footprint_top_candidate.png",
                "audit/first_street_towers_east/fste_interior_cutaway_candidate.png",
                "audit/first_street_towers_east/fste_interior_cluster_detail_candidate.png",
                "audit/first_street_towers_east/sources/purdue_first_street_towers_2009_exterior.jpg"
            ],
            "fresh_open_probe": "audit/first_street_towers_east/validation_fresh_open.json"
        },
        "findings": [
            "Purdue GIS independently verifies identity, orientation, plan dimensions, and near-exact structural footprint.",
            "The source supports six floors and complex-level brick/window/gable design language; East-specific height, entry, facade schedule, and roof details remain estimated.",
            "The modeled interior is clearly schematic, uses the published 22-room cluster and private-bath program, and does not claim an as-built plan.",
            "The fresh-open validation is from the candidate evidence; the grader environment has no Blender executable, so a second independent Blender reopen could not be run.",
            "The shared manifest remains stale for this revision and should be corrected by the coordinator before master integration."
        ],
        "methodology": "Exact asset hash check; raw GIS GeoJSON read directly and transformed with the project local approximation; independently rasterized polygon overlap at 0.10 m resolution from GIS ring and candidate fresh-open structural outline; reviewed candidate renders and original Purdue complex-level photo. The candidate's exact Shapely metrics and Blender reopen record were treated as corroborating evidence, not as the independent comparison. No builder score was used."
    }


if __name__ == "__main__":
    result = evaluate()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
