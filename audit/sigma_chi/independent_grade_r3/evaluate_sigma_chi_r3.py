"""Independent evidence evaluator for the frozen Sigma Chi FID 828 asset.

Run with standard Python. Blender was unavailable to this grader; the exact-hash
fresh-reopen report from the builder is checked and explicitly identified below.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / "modular/buildings/massing_sigma_chi_fid828.blend"
AUDIT = ROOT / "audit/sigma_chi"
OUT = Path(__file__).with_name("sigma_chi_independent_grade_r3.json")
EXPECTED_SHA = "f8f3fe8e061ce25b32e8cffa732c12d596a5af841887ea0d9d5752ebe2b8b4d7"
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137
XF = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
YF = 111040.0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def evaluate() -> dict:
    digest = sha256(ASSET)
    if digest != EXPECTED_SHA:
        raise RuntimeError(f"Frozen asset SHA mismatch: {digest}")

    with (AUDIT / "sources/purdue_gis_fid828_raw.json").open(encoding="utf-8") as stream:
        raw = json.load(stream)
    feature = next(
        item for item in raw["features"]
        if item.get("attributes", {}).get("FID") == 828
    )
    attrs = feature["attributes"]
    ring = feature["geometry"]["rings"][0]
    if ring[0] == ring[-1]:
        ring = ring[:-1]
    projected = [((lon - ORIGIN_LON) * XF, (lat - ORIGIN_LAT) * YF) for lon, lat in ring]
    bounds = [
        [min(point[axis] for point in projected), max(point[axis] for point in projected)]
        for axis in range(2)
    ]
    area = abs(sum(
        projected[i][0] * projected[(i + 1) % len(projected)][1]
        - projected[(i + 1) % len(projected)][0] * projected[i][1]
        for i in range(len(projected))
    )) / 2

    evidence = json.loads((AUDIT / "sigma_chi_evidence.json").read_text(encoding="utf-8"))
    reopen = json.loads((AUDIT / "fresh_reopen_validation.json").read_text(encoding="utf-8"))
    required_sources = [
        "sources/purdue_gis_fid828_raw.json",
        "sources/sigma_chi_chapter_house.html",
        "sources/sigma_chi_renovation.html",
        "sources/house_1960_62.gif",
        "sources/renovation_sept2006.jpg",
        "sigma_chi_fresh_reopen_render.png",
        "sigma_chi_front_oblique.png",
        "sigma_chi_roof_plan.png",
    ]
    source_coverage = {path: (AUDIT / path).is_file() for path in required_sources}
    if not all(source_coverage.values()):
        raise RuntimeError("Required source/render evidence missing")
    if reopen.get("asset_sha256") != digest or evidence.get("candidate_sha256") != digest:
        raise RuntimeError("Reopen/evidence records do not match the frozen asset SHA")

    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                f"Raw Purdue GIS FID {attrs['FID']} identifies {attrs['BUILDING_N']} at {attrs['ADDRESS']}; the chapter house page directly matches name and address.",
                f"GIS source contains {len(projected)} unique ring vertices; independent project conversion gives bounds X {bounds[0][0]:.3f}..{bounds[0][1]:.3f} m, Y {bounds[1][0]:.3f}..{bounds[1][1]:.3f} m and polygon area {area:.3f} m².",
                f"Matching-SHA fresh-reopen report records a six-vertex wall comparison with max XY error {reopen['gis_footprint_max_xy_error_m']:.8f} m.",
            ],
            "findings": [],
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                "The saved wall plan is reported compared against the complete transformed Purdue GIS ring; the transformed source controls campus position, orientation, and plan dimensions.",
                "The local project conversion is approximate and is not a surveyed CRS; no independent survey was found to compare against.",
            ],
            "findings": ["Horizontal dimensions and placement are verified to the Purdue GIS source, not an independent survey."],
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "score": 1.0,
            "max_score": 2,
            "evidence": [
                "The inspected candidate render and roof view show multiple gables, dormers, chimneys, and a steep roof, consistent with broad cues in the preserved chapter photos.",
                "Eaves (8.8 m), primary ridge (13.1 m), and chimney tops (16.96 m) are estimates; no elevation drawing, point cloud, or survey establishes height.",
                "GIS floor attributes say one level but conflict with the visible multi-storey house; modeled floor count remains unverified.",
            ],
            "findings": ["Height and floor count remain unverified. Roof form is recognizable but the modeled gable layout remains schematic versus the historic photos."],
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 1.25,
            "max_score": 2,
            "evidence": [
                "The inspected render includes an entry porch, grouped and divided windows, an arched gable opening, gabled roof breaks, and chimneys.",
                "The 1960–62 and 2006 construction photographs show a more irregular Tudor Revival composition with substantial stone surrounds, timber framing, and complex gables.",
                "The model facade remains regular and flat in the render; the signature stone/timber treatment and historic entrance proportions are only weakly represented.",
            ],
            "findings": ["Facade details and overall composition remain simplified relative to the available photographs."],
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                f"Exact asset SHA verified: {digest}.",
                f"The exact-SHA Blender {reopen['blender_version']} reopen report records the expected scene and collection, {reopen['mesh_object_count']} mesh objects, zero nonmanifold/loose edges, and PASS.",
                "Required raw sources, provenance metadata, and inspection renders are present. The evidence record names the stable asset ID, expected collection, and asset path.",
                "The independent grader could not personally reopen the .blend because Blender CLI was absent and the live Blender addon was unreachable; this gate relies on the builder's matching-SHA fresh-reopen report.",
            ],
            "findings": [],
        },
    ]
    score = round(sum(item["score"] for item in criteria), 2)
    findings = [finding for item in criteria for finding in item["findings"]]
    result = {
        "building": "Sigma Chi Delta Delta chapter house (Purdue GIS FID 828)",
        "asset_path": "modular/buildings/massing_sigma_chi_fid828.blend",
        "asset_sha256": digest,
        "grader": "Independent source, GIS, matching-SHA validation-record, and rendered-view review; criterion scores assigned by this evaluator",
        "blender_version_in_builder_validation": reopen["blender_version"],
        "independent_fresh_reopen": False,
        "score": score,
        "max_score": 10,
        "criteria": criteria,
        "evidence": {
            "identity_attributes": {key: attrs.get(key) for key in ["FID", "BUILDING_N", "BLDG_ABBR", "ADDRESS", "OWNER", "GlobalID"]},
            "gis_unique_vertex_count": len(projected),
            "gis_transformed_bounds_xy_m": bounds,
            "gis_projected_polygon_area_m2": area,
            "reported_wall_ring_max_xy_error_m": reopen["gis_footprint_max_xy_error_m"],
            "reported_mesh_object_count": reopen["mesh_object_count"],
            "reported_nonmanifold_edges": reopen["nonmanifold_mesh_edges"],
            "reported_loose_edges": reopen["loose_mesh_edges"],
            "source_and_render_coverage": source_coverage,
            "inspected_views": [
                "audit/sigma_chi/sigma_chi_fresh_reopen_render.png",
                "audit/sigma_chi/sigma_chi_front_oblique.png",
                "audit/sigma_chi/sigma_chi_roof_plan.png",
                "audit/sigma_chi/sources/house_1960_62.gif",
                "audit/sigma_chi/sources/renovation_sept2006.jpg",
            ],
            "independent_runtime_limitation": "Blender executable unavailable on PATH/standard installation locations; live Blender MCP connection failed. The matching-SHA builder report is used for reopen/topology gate only.",
        },
        "findings": findings,
        "pass_threshold": 8,
        "result": "PASS" if score >= 8 else "FAIL",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    evaluate()
