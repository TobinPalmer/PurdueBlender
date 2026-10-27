"""Independent rubric evaluator for VMIF asset revision 2."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def evaluate() -> dict:
    probe = json.loads((HERE / "fresh_open_probe.json").read_text(encoding="utf-8"))
    gis = json.loads((HERE / "gis_comparison.json").read_text(encoding="utf-8"))
    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2,
            "evidence": (
                "The fresh-open shell was compared to all 12 vertices of Purdue GIS BuildingShapesZip4 FID 78. "
                f"Maximum nearest-shell-vertex error is {gis['ring_vertex_max_distance_to_shell_mesh_m']:.6f} m. "
                "The source ring is preserved. GIS Shape__Area (849.074 m2) conflicts with coordinate-derived "
                f"ring area ({gis['ring_area_projected_m2']:.3f} m2), an unresolved source-data inconsistency."
            ),
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 2.0,
            "max_score": 2,
            "evidence": (
                "The stored anchor and independently projected GIS polygon centroid differ by "
                f"{gis['anchor_centroid_error_m']:.6f} m. Source corners align with the shell within "
                f"{gis['ring_vertex_max_distance_to_shell_mesh_m']:.6f} m; bounds are "
                f"{gis['dimensions_local_xy_m'][0]:.2f} x {gis['dimensions_local_xy_m'][1]:.2f} m. "
                "This grade verifies the modular local frame, not placement in the campus master."
            ),
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 1.5,
            "max_score": 2,
            "evidence": (
                "The evidence supports one story and aerial roof plan with a white low-slope roof and two rooftop "
                "plant masses. The saved asset is 4.52 m tall overall. Eave/roof elevations are explicit estimates; "
                "the GIS extrusion field has undocumented units and no target-specific exterior elevation was found."
            ),
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1.0,
            "max_score": 2,
            "evidence": (
                "Revision 2 adds a west service-door opening and leaf, plus documented interior stall doors and "
                "viewing windows. The service door's exact location is inferred; no exterior windows or target-specific "
                "facade elevations are evidenced. Visual inspection shows a largely plain, generic exterior with flat "
                "color materials and little visible facade articulation."
            ),
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 2.0,
            "max_score": 2,
            "evidence": (
                f"Fresh open succeeded in Blender {probe['blender_version']}; the named scene/collection contain "
                f"{probe['mesh_count']} meshes and {probe['material_count']} materials. There are no images, linked "
                "libraries, or materialless meshes. Building-specific source snapshots, evidence, preview/cutaway, "
                "and fresh-open validation are present."
            ),
        },
    ]
    score = round(sum(item["score"] for item in criteria), 2)
    return {
        "score": score,
        "max_score": 10,
        "passing_threshold": 8,
        "pass": score >= 8,
        "criteria": criteria,
        "evidence": {
            "asset": "modular/buildings/massing_veterinary_medicine_isolation_facility_66d1305.blend",
            "asset_sha256": probe["asset_sha256"],
            "fresh_open_probe": "audit/veterinary_medicine_isolation_facility/independent_grade_r2/fresh_open_probe.json",
            "gis_comparison": "audit/veterinary_medicine_isolation_facility/independent_grade_r2/gis_comparison.json",
            "independent_render": "audit/veterinary_medicine_isolation_facility/independent_grade_r2/exterior_material_render.png",
            "reference_preview": "audit/veterinary_medicine_isolation_facility/vmif_preview.png",
            "reference_cutaway": "audit/veterinary_medicine_isolation_facility/vmif_cutaway.png",
        },
        "findings": [
            "The GIS footprint is reproduced with sub-millimeter vertex agreement and the local anchor aligns with the independently calculated polygon centroid.",
            "The GIS Shape__Area field materially conflicts with the area computed from its own polygon vertices; the model follows the source outline and is not rescaled to the inconsistent field.",
            "Roof plan and one-story form have supporting evidence, but eave height, roof elevation, and the inferred service-door position remain uncertain.",
            "The new service opening addresses the previous exterior-access gap, while the facade still reads as a mostly plain mass with little evidence-backed exterior articulation.",
            "This grade is for the standalone modular asset; campus-master linking and neighboring-context placement were not assessed.",
        ],
    }


if __name__ == "__main__":
    result = evaluate()
    (HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
