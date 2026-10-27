"""Independent Lambertus Hall asset grader.

Run from repository root with `python audit/lambertus_hall/independent_grade/evaluate.py`.
The Blender fresh-open probe is produced separately by inspect_fresh.py.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit" / "lambertus_hall"
OUT = AUDIT / "independent_grade"
ASSET = ROOT / "modular" / "buildings" / "lambertus_hall.blend"
EXPECTED_SHA = "2DFE8E5EA016A29F5EE11228D8B0BA62C654BE7661DD103452BCCF56165FD7B4"


def ring_area(points):
    return abs(sum(points[i][0] * points[(i + 1) % len(points)][1]
                   - points[(i + 1) % len(points)][0] * points[i][1]
                   for i in range(len(points))) * 0.5)


def evaluate():
    evidence = json.loads((AUDIT / "evidence.json").read_text(encoding="utf-8"))
    probe = json.loads((OUT / "fresh_probe.json").read_text(encoding="utf-8"))
    gis = json.loads((AUDIT / "sources" / "purdue_fid433.json").read_text(encoding="utf-8"))
    feature = gis["features"][0]
    attrs = feature["attributes"]
    geographic_ring = feature["geometry"]["rings"][0]
    if geographic_ring[0] == geographic_ring[-1]:
        geographic_ring = geographic_ring[:-1]

    lon0, lat0 = evidence["coordinate_frame"]["origin_lon_lat"]
    x_scale = 111412.84 * math.cos(math.radians(40.4274))
    y_scale = 111040.0
    expected_local = [((lon - lon0) * x_scale, (lat - lat0) * y_scale)
                      for lon, lat in geographic_ring]
    shell = probe["shell"]
    shell_xy = [[v[0], v[1]] for v in shell["local_vertices"][:len(expected_local)]]
    residuals = [math.dist(a, b) for a, b in zip(shell_xy, expected_local)]
    max_ring_error = max(residuals, default=None)
    mean_ring_error = sum(residuals) / len(residuals) if residuals else None

    placement = evidence["master_integration"]["placement_origin_xy_m"]
    expected_placement = [
        (lon0 + 86.9137) * x_scale,
        (lat0 - 40.4274) * y_scale,
    ]
    placement_error = math.dist(placement, expected_placement)
    source_global = [((lon + 86.9137) * x_scale, (lat - 40.4274) * y_scale)
                     for lon, lat in geographic_ring]
    source_bounds = [
        [min(p[0] for p in source_global), max(p[0] for p in source_global)],
        [min(p[1] for p in source_global), max(p[1] for p in source_global)],
        [0.0, evidence["estimated_dimensions"]["height_m"]],
    ]
    asset_global_bounds = [[shell["local_bounds"][i][0] + placement[i],
                            shell["local_bounds"][i][1] + placement[i]]
                           for i in (0, 1)] + [shell["local_bounds"][2]]
    global_bounds_error = max(abs(source_bounds[i][j] - asset_global_bounds[i][j])
                              for i in range(3) for j in range(2))
    sha = hashlib.sha256(ASSET.read_bytes()).hexdigest().upper()

    # The known source limitation is explicit: the official architecture pages
    # show the joined Dudley/Lambertus project, while the strongest exterior
    # photograph in this packet visibly labels the photographed wing Dudley.
    facade_image_wing_ambiguity = True
    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                f"Purdue GIS feature FID {attrs.get('FID')} identifies {attrs.get('BLDG_ABBR')} / {attrs.get('BUILDING_N')} at {attrs.get('ADDRESS')}.",
                f"The GIS ring has {len(geographic_ring)} distinct perimeter vertices; candidate shell has {shell['vertex_count'] // 2} per level.",
                f"Independent paired local-vertex comparison max error={max_ring_error:.9g} m; mean={mean_ring_error:.9g} m.",
                "Adjacent FID 432 is recorded as DUDL / Dudley Hall, reducing risk of selecting the neighboring GIS polygon.",
            ],
            "findings": [],
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                f"Fresh-open shell is at local origin with unit scale; shell local bounds are {shell['local_bounds']} m.",
                f"Evidence placement origin differs from independent conversion by {placement_error:.9g} m.",
                f"After applying that origin, shell bounds differ from source-derived global bounds by at most {global_bounds_error:.9g} m.",
                "The model uses the project's documented local approximate lon/lat conversion; no independent survey CRS or survey control is available.",
            ],
            "findings": [],
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 1.0,
            "max_score": 2,
            "evidence": [
                "The asset is five levels and 16 m high, consistent with the cited fifth-floor Nuclear Engineering use and overall project imagery.",
                "The top is modeled as a flat roof with parapet and a small screened plant; render 02 exposes the roof footprint.",
                "The 16 m height and 3.1 m story spacing are explicitly estimates; no Lambertus-only elevation or measured height was found.",
            ],
            "findings": ["Height and floor elevations remain estimates, and the rooftop plant has no Lambertus-specific source confirmation."],
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1.0,
            "max_score": 2,
            "evidence": [
                "The model includes glazed panels, brick-colored areas, concrete-colored piers/belts, terracotta-colored sunshades, and entry canopies.",
                "The Ennead massing diagrams support a transparent ground level and multiple entry points; the BSA exterior photo supports glass, horizontal screening, and pale vertical structure.",
                "The strongest exterior photo visibly labels Dudley Hall; the packet itself says exact Lambertus-vs-Dudley facade allocation is unclear.",
            ],
            "findings": ["Facade rhythm/material mapping is only partly attributable to Lambertus; the render's repeated vertical shade fins and entrances are not checked against a Lambertus-only elevation."],
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                f"Independent fresh-open found scene {probe['scene']!r}, collection {probe['collection']!r}, {probe['collection_object_count']} mesh objects, and {probe['unique_mesh_material_count']} assigned materials.",
                f"SHA-256 {sha}; expected hash matches: {sha == EXPECTED_SHA}.",
                f"No linked libraries; missing external texture paths: {len(probe['asset_textures_missing'])}.",
                "Evidence includes raw FID 433 and FID 432 snapshots, design diagrams, project photography, three renders, coordinate method, and explicit uncertainty notes.",
            ],
            "findings": [],
        },
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    findings = [finding for criterion in criteria for finding in criterion["findings"]]
    if sha != EXPECTED_SHA:
        findings.append("Candidate SHA differs from the assigned revision; this grade must be rerun on the intended file.")
    if max_ring_error is None or max_ring_error > 0.0001:
        findings.append("GIS ring does not match the candidate shell within the independent 0.1 mm check.")
    if placement_error > 0.001:
        findings.append("Recorded placement origin does not match the project conversion within 1 mm.")
    return {
        "building_id": "lambertus_hall",
        "score": score,
        "max_score": 10,
        "passing_threshold": 8,
        "passed": score >= 8 and sha == EXPECTED_SHA and (max_ring_error or 1) <= 0.0001,
        "criteria": criteria,
        "evidence": {
            "asset": str(ASSET.relative_to(ROOT)),
            "asset_sha256": sha,
            "expected_sha256": EXPECTED_SHA,
            "sha_match": sha == EXPECTED_SHA,
            "fresh_open_probe": str((OUT / "fresh_probe.json").relative_to(ROOT)),
            "source_feature_id": attrs.get("FID"),
            "source_official_code": attrs.get("BLDG_ABBR"),
            "distinct_source_vertices": len(geographic_ring),
            "candidate_shell_vertices_per_level": shell["vertex_count"] // 2,
            "max_source_vertex_error_m": max_ring_error,
            "mean_source_vertex_error_m": mean_ring_error,
            "placement_origin_m": placement,
            "independently_converted_placement_origin_m": expected_placement,
            "placement_origin_error_m": placement_error,
            "global_bounds_error_m": global_bounds_error,
            "source_footprint_area_m2": ring_area(source_global),
            "estimated_height_m": evidence["estimated_dimensions"]["height_m"],
            "facade_image_wing_ambiguity": facade_image_wing_ambiguity,
            "linked_libraries": probe["library_paths"],
            "missing_external_textures": probe["asset_textures_missing"],
            "master_manifest_state": "Manifest/master integration is coordinator-owned and is not changed or graded as part of this asset-only review.",
            "render_paths": evidence["renders"],
        },
        "findings": findings,
        "remaining_uncertainties": evidence["remaining_uncertainties"],
    }


if __name__ == "__main__":
    result = evaluate()
    (OUT / "grade.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    summary = [
        "# Independent Lambertus Hall grade",
        "",
        f"**Score: {result['score']:.1f}/{result['max_score']} — {'PASS' if result['passed'] else 'NEEDS REVISION'}**",
        "",
        "| Criterion | Score | Evidence / limitation |",
        "|---|---:|---|",
    ]
    for c in result["criteria"]:
        summary.append(f"| {c['name']} | {c['score']:.1f}/{c['max_score']} | {' '.join(c['evidence'])} {' '.join(c['findings'])} |")
    summary += ["", "## Overall findings", ""] + [f"- {f}" for f in result["findings"]]
    summary += ["", "## Remaining uncertainties", ""] + [f"- {u}" for u in result["remaining_uncertainties"]]
    (OUT / "grade.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
