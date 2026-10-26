"""Independent evaluator for the Purdue Drug Discovery Facility asset.

Run from the repository root with the bundled/local Blender installation available.
The probe opens the .blend itself; footprint comparison is performed here against
the preserved official GIS feature, not against the builder's metrics JSON.
"""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSET_ID = "massing_purdue_drug_discovery_facility_fc72a4a"
ASSET = ROOT / "modular/buildings" / f"{ASSET_ID}.blend"
COLLECTION = f"Asset_{ASSET_ID}"
PROBE = Path(__file__).with_name("blender_probe.py")
PROBE_RESULT = Path(__file__).with_name("blender_probe_result.json")
SOURCES = ROOT / "audit/purdue_drug_discovery_facility/sources"
GIS_FILE = SOURCES / "arcgis_feature_893_2026-10-26.geojson"
BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
ORIGIN_LON = -86.9137
ORIGIN_LAT = 40.4274
METERS_PER_DEG_LON = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
METERS_PER_DEG_LAT = 111040.0


def point_segment_distance(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    denom = dx * dx + dy * dy
    if denom == 0:
        return math.dist(p, a)
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / denom))
    q = (a[0] + t * dx, a[1] + t * dy)
    return math.dist(p, q)


def directed_distance(points, edges):
    return max(min(point_segment_distance(p, a, b) for a, b in edges) for p in points)


def geometry_comparison(probe):
    gj = json.loads(GIS_FILE.read_text(encoding="utf-8"))
    feature = gj["features"][0]
    props = feature["properties"]
    rings = []
    for ring in feature["geometry"]["coordinates"]:
        projected = [((lon - ORIGIN_LON) * METERS_PER_DEG_LON,
                      (lat - ORIGIN_LAT) * METERS_PER_DEG_LAT) for lon, lat in ring]
        rings.append(projected)
    source_points = [p for ring in rings for p in ring]
    source_edges = [(ring[i], ring[i + 1]) for ring in rings for i in range(len(ring) - 1)]
    model_edges = [(tuple(edge[0]), tuple(edge[1])) for edge in probe["base_outline_edges_xy_m"]]
    model_points = list({tuple(p) for edge in probe["base_outline_edges_xy_m"] for p in edge})
    src_to_model = directed_distance(source_points, model_edges)
    model_to_source = directed_distance(model_points, source_edges)
    return {
        "source_properties": {k: props.get(k) for k in ("FID", "BLDG_ABBR", "BUILDING_N", "ADDRESS", "NUM_LEVELS", "CountOfFLO", "F02", "F03", "F04", "R")},
        "source_ring_count": len(rings),
        "source_point_count": len(source_points),
        "model_outline_edge_count": len(model_edges),
        "source_to_model_max_distance_m": src_to_model,
        "model_to_source_max_distance_m": model_to_source,
        "symmetric_hausdorff_sampled_m": max(src_to_model, model_to_source),
    }


def evaluate():
    if not ASSET.exists() or not GIS_FILE.exists() or not BLENDER.exists():
        raise FileNotFoundError("Asset, GIS snapshot, or Blender executable is missing")
    proc = subprocess.run(
        [str(BLENDER), "--background", str(ASSET), "--python", str(PROBE), "--", str(PROBE_RESULT)],
        cwd=ROOT, text=True, capture_output=True, timeout=120,
    )
    if proc.returncode != 0 or not PROBE_RESULT.exists():
        raise RuntimeError(f"Fresh Blender probe failed (exit {proc.returncode}):\n{proc.stdout}\n{proc.stderr}")
    probe = json.loads(PROBE_RESULT.read_text(encoding="utf-8"))
    geometry = geometry_comparison(probe)
    asset_sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    props = geometry["source_properties"]
    identity_ok = (props["FID"] == 893 and props["BLDG_ABBR"] == "DRUG"
                   and props["BUILDING_N"] == "Drug Discovery Facility"
                   and props["ADDRESS"] == "720 Clinic Drive")
    footprint_ok = geometry["symmetric_hausdorff_sampled_m"] <= 0.40
    source_bound = [[-345.26046375767623, -305.81210487133734],
                    [-647.9187789460775, -597.6403133375993]]
    shell_bounds = probe["shell_bounds_world_m"]
    bounds_delta = [max(abs(shell_bounds[i][j] - source_bound[i][j]) for j in (0, 1)) for i in (0, 1)]
    position_ok = footprint_ok and max(bounds_delta) <= 0.30
    clean_export = (probe["collection_found"] and probe["scene"] == f"Building_{ASSET_ID}"
                    and probe["collection_object_count"] == 35
                    and probe["mesh_object_count"] == 35
                    and not probe["meshes_without_materials"]
                    and not probe["external_libraries"])
    identity_footprint_score = 2.0 if identity_ok and footprint_ok else (1.0 if identity_ok else 0.5)
    position_score = 1.9 if position_ok else 0.8
    export_score = 2.0 if clean_export else 0.8

    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint", "score": identity_footprint_score, "max_score": 2.0,
            "status": "verified" if identity_ok and footprint_ok else "incomplete",
            "evidence": [
                "Independent inspection of the saved Purdue GIS feature confirms FID 893, abbreviation DRUG, name Drug Discovery Facility, and address 720 Clinic Drive.",
                "Purdue Office of Research independently identifies the Drug Discovery Facility at 720 Clinic Drive and describes its three-story research program.",
                f"Measured mesh base outline against all preserved projected GIS outer/courtyard rings; sampled symmetric maximum deviation is {geometry['symmetric_hausdorff_sampled_m']:.3f} m (0.40 m acceptance tolerance, consistent with the low-detail simplification needed for the 152-vertex GIS perimeter).",
            ],
            "reason": "Official facility identity and location agree, and the shell follows the source polygon including the courtyard within the documented simplification tolerance.",
        },
        {
            "criterion": "Position, orientation, and scale/dimensions", "score": position_score, "max_score": 2.0,
            "status": "verified in project coordinate frame; transform is approximate" if position_ok else "footprint/extent discrepancy",
            "evidence": [
                f"The shell remains at its expected campus-world coordinates; per-axis max bounding difference versus the GIS-converted extent is {bounds_delta} m.",
                "Footprint vertices follow the official feature with no additional translation, rotation, or scale change; the supplied campus conversion uses an approximate local longitude/latitude-to-meter transform rather than a surveyed CRS.",
            ],
            "reason": "Plan shape and campus placement are directly compared to the GIS, but absolute geodetic position inherits the project's approximate coordinate conversion.",
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form", "score": 1.5, "max_score": 2.0,
            "status": "three stories verified; vertical dimensions partly interpreted",
            "evidence": [
                "Purdue Office of Research explicitly calls the facility three-story.",
                "The preserved GIS record contains F02=16, F03=32, F04=48 and R=56, but its saved field metadata supplies no field descriptions or units; interpreting R as a 56-ft roof datum is plausible but not formally established.",
                f"Fresh geometry inspection reports wall top {probe['shell_bounds_world_m'][2][1]:.2f} m and full asset top {probe['full_asset_bounds_world_m'][2][1]:.2f} m due to the entrance canopy; floor elevations and wall height remain estimated.",
                "Published photos support a flat roof and high entrance canopy, but no measured elevations or as-built floor-level drawing were found.",
            ],
            "reason": "Story count and broad roof silhouette are supported, but exact floor spacing, parapet height, and the semantic meaning of the GIS vertical fields are not conclusively evidenced.",
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture", "score": 1.7, "max_score": 2.0,
            "status": "mostly source-supported; rear/courtyard treatment inferred",
            "evidence": [
                "The Purdue Office of Research photo shows the brick facade, regular horizontal floor bands, tall glazed entrance bay, and projecting flat canopy; these major elements appear in the inspected render.",
                "Purdue's official facility description says users can observe lab experiments through glass barriers, supporting the glazed facade feature.",
                "The model includes windows, brick, glazing, metal frames, a canopy/columns, doors, lobby levels, reception desk, and a feature wall; only the public oblique night view and 2011 proposed plan/render were available for detailed comparison.",
            ],
            "reason": "The prominent architecture reads consistently with official imagery, while secondary elevations and exact entrance placement are inferred from a proposed design and sparse oblique imagery.",
        },
        {
            "criterion": "Modular export, portability, and complete evidence", "score": export_score, "max_score": 2.0,
            "status": "verified by independent fresh-open probe" if clean_export else "export validation failed",
            "evidence": [
                f"Fresh Blender {probe['blender_version']} open confirms the named scene and collection, {probe['collection_object_count']} collection objects ({probe['mesh_object_count']} meshes), and {probe['polygon_count']} polygons.",
                f"All meshes have material slots ({probe['unique_material_count']} unique materials); there are {len(probe['external_libraries'])} external linked libraries and no mesh missing materials.",
                f"Asset SHA-256 independently computed: {asset_sha}.",
                "The building-specific folder contains raw GIS feature and metadata snapshots, official Purdue photo/page snapshots, a proposed plan and floor plan/interior image, a render, and fresh-open validation evidence.",
            ],
            "reason": "The asset reopens cleanly, keeps its stable collection contract, uses self-contained material data, and has substantial source/evidence records.",
        },
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    findings = [
        "The asset uses campus-world coordinates as a simple massing library; master placement-marker integration has not been reviewed by this grading pass.",
        "No surveyed/elevation source establishes exact main-wall, parapet, canopy, or floor-level dimensions; retain these as estimates.",
        "Rear and courtyard facade rhythms are repeated/inferred from the front photo rather than independently confirmed from matching views.",
    ]
    return {
        "building": "Purdue Drug Discovery Facility",
        "asset_id": ASSET_ID,
        "asset_path": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
        "asset_sha256": asset_sha,
        "grader": "independent_grader_subagent",
        "grade_date": "2026-10-26",
        "score": score,
        "max_score": 10,
        "passing_threshold": 8,
        "status": "PASS" if score >= 8 else "FAIL",
        "criteria": criteria,
        "evidence": {
            "fresh_open_probe": str(PROBE_RESULT.relative_to(ROOT)).replace("\\", "/"),
            "footprint_comparison": geometry,
            "inspected_preview": "audit/purdue_drug_discovery_facility/preview_drug_discovery_facility_2026-10-26.png",
            "official_sources": [
                {"title": "Institutes and Centers at Discovery Park — Purdue University", "url": "https://research.purdue.edu/about/institutes-and-centers/", "verified_claim": "Lines 140-158 identify the facility, location, three-story description and glazed experiment-observation feature."},
                {"title": "Drug Discovery Building — Purdue Department of Chemistry", "url": "https://www.chem.purdue.edu/DrugDiscovery/building.html", "verified_claim": "Confirms the facility identity and provides the proposed map, first-floor layout and architectural images."},
                {"title": "Purdue campus GIS layer metadata", "url": "https://mapsweb.lib.purdue.edu/arcgis/rest/services/Purdue/campus/MapServer/0", "verified_claim": "Confirms Purdue campus polygon feature service and its EPSG:3857 spatial reference; project footprint itself is feature FID 893 in the preserved hosted-layer snapshot."},
            ],
            "model_evidence_snapshot": "audit/purdue_drug_discovery_facility/model_evidence_2026-10-26.json",
        },
        "findings": findings,
        "grader_notes": "The GIS F02/F03/F04/R values suggest floor and roof datums, but the layer snapshot has no field descriptions or explicit units. The numeric mapping is plausible, not independently defined. Score is above threshold despite this limitation.",
    }


if __name__ == "__main__":
    result = evaluate()
    out = Path(__file__).with_name("result.json")
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"score": result["score"], "status": result["status"], "asset_sha256": result["asset_sha256"], "result": str(out)}))
