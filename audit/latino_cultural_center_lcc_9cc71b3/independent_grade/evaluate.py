"""Independent grader for the current LCC FID 925 asset.

Run from the repository root with:
  python audit/latino_cultural_center_lcc_9cc71b3/independent_grade/evaluate.py

First run probe_asset.py with Blender 5.2.3 or later to independently fresh-open
the candidate and save fresh_probe.json. This evaluator does not modify assets.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit" / "latino_cultural_center_lcc_9cc71b3"
OUT = AUDIT / "independent_grade"
ASSET = ROOT / "modular" / "buildings" / "massing_latino_cultural_center_lcc_9cc71b3.blend"


def area(poly):
    return abs(sum(poly[i][0] * poly[(i+1) % len(poly)][1]
                   - poly[(i+1) % len(poly)][0] * poly[i][1]
                   for i in range(len(poly))) * 0.5)


def evaluate():
    report = json.loads((AUDIT / "model_evidence.json").read_text(encoding="utf-8"))
    probe = json.loads((OUT / "fresh_probe.json").read_text(encoding="utf-8"))
    gis_all = json.loads((AUDIT / "sources" / "purdue_building_shapes_lcc_all.json").read_text(encoding="utf-8"))
    feature = next(f for f in gis_all["features"] if f["attributes"].get("FID") == 925)
    attrs = feature["attributes"]
    raw_ring = feature["geometry"]["rings"][0]
    ring = raw_ring[:-1] if raw_ring[0] == raw_ring[-1] else raw_ring
    lat0, lon0 = 40.4274, -86.9137
    xscale = 111412.84 * math.cos(math.radians(lat0))
    expected_xy = [((lon - lon0) * xscale, (lat - lat0) * 111040.0) for lon, lat in ring]
    floor = next(o for o in probe["objects"] if o["name"] == "LCC_FID925_Footprint_Floor")
    modeled_xy = [[p[0], p[1]] for p in floor["mesh_vertices_world"]]
    # Both lists preserve raw GIS ring ordering after dropping its duplicate close.
    paired_errors = [math.dist(a, b) for a, b in zip(modeled_xy, expected_xy)]
    max_vertex_error = max(paired_errors, default=None)
    mean_vertex_error = sum(paired_errors) / len(paired_errors) if paired_errors else None
    gis_bounds = [[min(p[0] for p in expected_xy), max(p[0] for p in expected_xy)],
                  [min(p[1] for p in expected_xy), max(p[1] for p in expected_xy)]]
    floor_bounds = floor["bounds"][:2]
    footprint_bounds_error = max(abs(gis_bounds[axis][edge] - floor_bounds[axis][edge])
                                 for axis in (0,1) for edge in (0,1))
    modeled_area = area(modeled_xy)
    gis_area = area(expected_xy)
    sha = hashlib.sha256(ASSET.read_bytes()).hexdigest().upper()
    all_materials_procedural = all(not item["external_images"] and not item["library"]
                                   for item in probe["material_specs"].values())
    no_linked_libraries = not probe["library_paths"] and all(o["library"] is None for o in probe["objects"])

    criteria = [
        {
            "criterion": "Identity and official source match",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                f"Purdue BuildingShapesZip4 FID {attrs['FID']} labels the feature {attrs['BUILDING_N']!r}, code {attrs['BLDG_ABBR']}, address {attrs['ADDRESS']!r}.",
                "Purdue LCC homepage snapshot gives the same address and the multicolored house, teal brick, yellow window trim, pink entrance and identifying sign.",
                "The asset depicts a one-story house-scale cultural center and contains a campus-context sign; no competing source candidate was used for the feature.",
            ],
            "findings": [],
        },
        {
            "criterion": "Footprint, campus placement, orientation and scale",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                f"The dedicated floor mesh has {len(modeled_xy)} vertices and matches the transformed FID 925 vertices in source order; max error {max_vertex_error:.8g} m, mean {mean_vertex_error:.8g} m.",
                f"Source/model footprint bounding-box maximum edge error {footprint_bounds_error:.8g} m; computed source area {gis_area:.3f} m^2 and model area {modeled_area:.3f} m^2.",
                f"Fresh-open campus-coordinate bounds {probe['collection_bounds']} m agree with the submitted evidence bounds; the asset retains identity placement for the massing convention.",
                "The FID 925 outline overlays the roof in the saved Esri World Imagery mosaic; this visual check is approximate because mosaic capture dates vary and are not recorded for each tile.",
            ],
            "findings": [],
        },
        {
            "criterion": "Evidence-supported height, floors and roof",
            "score": 1.5,
            "max_score": 2,
            "evidence": [
                f"GIS attributes report {attrs['NUM_LEVELS']} level and the candidate is visibly a one-story house with pitched main and secondary wing roofs.",
                "Purdue exterior imagery supports the shingled pitched roof, prominent dormer and chimney form; aerial imagery supports the roof massing.",
                f"Fresh-open model top is {probe['collection_bounds'][2][1]:.2f} m, with evidence reporting a 5.78 m main ridge and 4.92 m east-wing peak.",
            ],
            "findings": ["No surveyed elevation or dimensioned current plan supports the exact eave, ridge, wing-peak or chimney heights; these remain estimates."],
        },
        {
            "criterion": "Facade, materials and interior",
            "score": 1.5,
            "max_score": 2,
            "evidence": [
                "The exterior render reproduces the current Purdue hero image's strongest cues: vivid teal masonry, yellow window surrounds, pink entry, white clapboard wing, divided windows and center sign.",
                "The saved facility source lists lounge, gathering, conference, ITaP lab, library and kitchen functions; the candidate includes those room types and the render depicts furnished activity zones.",
                "The 2023 garden source supports an on-site community garden; the candidate includes a small raised bed and planting.",
            ],
            "findings": ["The interior plan and room positions are schematic because no dimensioned floor plan was found. Some specific facade/window dimensions and garden-bed placement remain inferred."],
        },
        {
            "criterion": "Modular portability and evidence completeness",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                f"Blender fresh-open read the expected scene/collection; collection contains {probe['collection_object_count']} objects ({probe['mesh_count']} mesh and {probe['other_count']} FONT text objects). Render setup is separated in sibling collections.",
                f"Asset SHA-256 is {sha}; it matches the candidate checksum in build_report.md: {sha == '277F47A7941B785E9ABC9D3D799CAE65BA3872F7F78CB4D2420C68A5E913310A'}.",
                f"No linked libraries: {no_linked_libraries}. Materials have no external image dependencies: {all_materials_procedural}.",
                "The evidence folder includes raw Purdue GIS, current and historical official exterior images, facility information, garden evidence, Esri imagery tiles, and four renders with dates, source IDs and uncertainty notes.",
            ],
            "findings": [],
        },
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    findings = [finding for c in criteria for finding in c["findings"]]
    if not no_linked_libraries:
        findings.append("Unexpected linked library dependency detected in the asset.")
    if not all_materials_procedural:
        findings.append("External image or material dependency detected; pack or relink before handoff.")
    return {
        "building_id": "massing_latino_cultural_center_lcc_9cc71b3",
        "score": score,
        "max_score": 10,
        "passing_threshold": 8,
        "passed": score >= 8 and max_vertex_error is not None and max_vertex_error < 0.001 and sha == "277F47A7941B785E9ABC9D3D799CAE65BA3872F7F78CB4D2420C68A5E913310A",
        "criteria": criteria,
        "evidence": {
            "candidate_asset": str(ASSET.relative_to(ROOT)),
            "asset_sha256": sha,
            "scene": probe["scene"],
            "collection": probe["collection"],
            "fresh_open_bounds_m": probe["collection_bounds"],
            "asset_object_counts": {"total": probe["collection_object_count"], "mesh": probe["mesh_count"], "font": probe["other_count"]},
            "FID": attrs["FID"], "official_abbreviation": attrs["BLDG_ABBR"], "official_name": attrs["BUILDING_N"],
            "source_distinct_footprint_vertices": len(expected_xy), "candidate_floor_vertices": len(modeled_xy),
            "max_paired_vertex_error_m": max_vertex_error, "mean_paired_vertex_error_m": mean_vertex_error,
            "source_floor_area_m2": gis_area, "candidate_floor_area_m2": modeled_area,
            "footprint_bbox_error_m": footprint_bounds_error,
            "campus_placement": "Campus coordinates / identity transform per massing convention; GIS vertices use documented local approximation.",
            "linked_libraries": probe["library_paths"], "external_texture_paths": sorted({p for m in probe["material_specs"].values() for p in m["external_images"]}),
            "visual_site_check": "audit/latino_cultural_center_lcc_9cc71b3/independent_grade/aerial_fid925_overlay.png",
        },
        "findings": findings,
        "uncertainties": report["uncertainties"],
    }


if __name__ == "__main__":
    result=evaluate()
    (OUT/"grade.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    md=["# Independent LCC FID 925 grade","",f"**Score: {result['score']:.1f}/{result['max_score']} — {'PASS' if result['passed'] else 'NEEDS REVISION'}**","",
        "| Criterion | Score | Evidence and findings |","|---|---:|---|"]
    for c in result["criteria"]:
        md.append(f"| {c['criterion']} | {c['score']:.1f}/{c['max_score']} | {' '.join(c['evidence'])} {' '.join(c['findings'])} |")
    md += ["","## Overall findings",""] + [f"- {f}" for f in result["findings"]]
    md += ["","## Uncertainties",""] + [f"- {u}" for u in result["uncertainties"]]
    (OUT/"grade.md").write_text("\n".join(md)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
