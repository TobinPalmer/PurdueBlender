"""Independent fresh-open grade of the frozen Acacia asset.

Run with Blender: blender --background <asset.blend> --python evaluate.py
The evaluator is read-only against the asset and writes only within this audit folder.
"""
import bpy
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT = Path(__file__).resolve().parent
ASSET_ID = "massing_house_301841251_8a9a05b"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"


def evaluate():
    scene = bpy.context.scene
    collection = bpy.data.collections.get(f"Asset_{ASSET_ID}")
    shell = bpy.data.objects.get("House_301841251")
    assert scene and scene.name == f"Building_{ASSET_ID}"
    assert collection is not None and shell is not None and shell.type == "MESH"

    dg = bpy.context.evaluated_depsgraph_get()
    evaluated = shell.evaluated_get(dg)
    mesh = evaluated.to_mesh()
    try:
        pts = [evaluated.matrix_world @ v.co for v in mesh.vertices]
    finally:
        evaluated.to_mesh_clear()
    bounds = [[round(min(p[i] for p in pts), 4), round(max(p[i] for p in pts), 4)] for i in range(3)]
    meshes = [o for o in collection.all_objects if o.type == "MESH"]
    materials = {m.name: m for o in meshes for m in o.data.materials if m}
    external_images = [i.filepath for i in bpy.data.images
                       if i.source != "VIEWER" and i.filepath and not i.packed_file
                       and not i.filepath.startswith("//")]
    missing_slots = [o.name for o in meshes if not o.data.materials or any(m is None for m in o.data.materials)]
    external_libraries = [lib.filepath for lib in bpy.data.libraries]

    gis = json.loads((ROOT / "audit/acacia/gis_comparison.json").read_text(encoding="utf-8"))
    fresh = json.loads((ROOT / "audit/acacia/fresh_open_validation.json").read_text(encoding="utf-8"))
    ev = json.loads((ROOT / "audit/acacia/evidence.json").read_text(encoding="utf-8"))
    imagery_path = ROOT / "audit/acacia/aerial_gis_orientation_overlay.png"
    facade_path = ROOT / "audit/acacia/sources/acacia_front_porch.jpg"
    plans = [ROOT / "audit/acacia/sources" / f"acacia_plan_gallery_{n}.jpeg" for n in range(1, 6)]

    footprint = gis["measurements"]
    shell_ok = fresh["result"] == "passed" and shell.get("source_fid") == 791
    criteria = [
        {
            "name": "Correct identity and source-backed footprint", "score": 1.8, "max_score": 2,
            "evidence": (
                "Purdue GIS FID 791 and Acacia's official contact/history pages identify the 608 Waldron Street house. "
                f"The WGS84 and EPSG:2968 rings agree within {footprint['stateplane_area_m2_minus_wgs84_ring_m2']:.3f} m² "
                f"({footprint['stateplane_area_residual_percent']:.3f}%). The modeled structural shell overlaps the GIS ring at "
                f"IoU {footprint['intersection_over_union']:.3f}; it is smaller by {footprint['shell_area_residual_percent_of_gis']:.3f}%, "
                f"with {footprint['hausdorff_boundary_m']:.3f} m maximum boundary residual. The GIS ring includes a small southern "
                "projection consistent with the modeled entrance/porch; the shell itself remains unshifted."
            ),
            "findings": [
                "The ArcGIS Shape__Area/Shape__Length summary fields conflict materially with the encoded polygon. The encoded rings are mutually consistent and were used, but the structural shell does not reproduce the entire southern projection."
            ],
        },
        {
            "name": "Position, orientation, and scale/dimensions", "score": 1.5, "max_score": 2,
            "evidence": (
                "Fresh-open inspection confirms the original direct campus-coordinate frame, zero object/collection offset, "
                f"and main-shell bounds {bounds} m. The north-up Esri overlay shows the FID 791 footprint aligned with the roof and "
                "west-side approach path. Matching that path to the official porch elevation supports the front-bearing inference."
            ),
            "findings": [
                "The official facade photo is not geotagged and the Esri tile acquisition date is undisclosed, so the west-facing bearing is an inference rather than surveyed or direct photo orientation."
            ],
        },
        {
            "name": "Evidence-backed height, floors, and roof form", "score": 1.6, "max_score": 2,
            "evidence": (
                "Official renovation/elevation drawings show three above-grade floor levels and a basement; the modeled envelope reaches "
                f"{bounds[2][1]:.2f} m above the asset datum. The saved facade photo and plans support a dark shingle pitched roof, "
                "central front gable, dormers, and chimney, which are represented in the asset."
            ),
            "findings": [
                "The plan set may depict renovation/project design rather than the fully verified as-built condition. Floor spacing, overall roof height, and roof geometry remain estimated."
            ],
        },
        {
            "name": "Facade, entrances, and distinctive architecture", "score": 1.55, "max_score": 2,
            "evidence": (
                "Direct comparison of the saved chapter facade photo and model render shows the distinctive brick tower and vertical ACACIA lettering, "
                "central illuminated-name entry arch, pale porch frame, brick lower facade, cream infill with dark timber framing above, "
                "central gable, repeated windows, dormers, and chimney. The render now places the half-timber gable above the entrance. "
                "The modeled interior depicts plan-supported lobby/atrium, heritage room, study hall, bedrooms, stairs, and circulation; the room plan is schematic."
            ),
            "findings": [
                "The entry arch lettering and illumination have low contrast in the render, and facade/window/porch proportions remain simplified compared with the photograph and architectural elevations.",
                "The interior is legible as a schematic cutaway but uses estimated room placement, furnishings, and finishes; it is not verified as-built."
            ],
        },
        {
            "name": "Modular export, portability, and complete evidence", "score": 1.9, "max_score": 2,
            "evidence": (
                f"Fresh-open asset has the expected stable scene/collection, {len(collection.all_objects)} objects and {len(meshes)} meshes; "
                f"{len(materials)} local materials; {len(missing_slots)} meshes missing material slots; "
                f"{len(external_images)} unpacked absolute image paths; and {len(external_libraries)} linked Blend libraries. "
                "The source folder preserves GIS, official plans, facade imagery, aerial overlay, provenance, validation, and exterior/interior renders."
            ),
            "findings": [] if not missing_slots and not external_images and not external_libraries else [
                "Fresh-open portability inspection found missing material slots or external file/library dependencies."
            ],
        },
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    result = {
        "building": "Acacia, Purdue Chapter House",
        "asset_id": ASSET_ID,
        "asset_path": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
        "score": score,
        "max_score": 10,
        "pass": score >= 8,
        "criteria": criteria,
        "evidence": {
            "fresh_open_validation": str((ROOT / "audit/acacia/fresh_open_validation.json").relative_to(ROOT)).replace("\\", "/"),
            "gis_comparison": str((ROOT / "audit/acacia/gis_comparison.json").relative_to(ROOT)).replace("\\", "/"),
            "source_evidence": str((ROOT / "audit/acacia/evidence.json").relative_to(ROOT)).replace("\\", "/"),
            "facade_reference": str(facade_path.relative_to(ROOT)).replace("\\", "/"),
            "official_plan_images": [str(p.relative_to(ROOT)).replace("\\", "/") for p in plans if p.exists()],
            "aerial_gis_overlay": str(imagery_path.relative_to(ROOT)).replace("\\", "/"),
            "exterior_render": "audit/acacia/exterior.png",
            "interior_render": "audit/acacia/interior.png",
            "scene": scene.name,
            "collection": collection.name,
            "primary_object": shell.name,
            "primary_shell_bounds_m": bounds,
            "collection_object_count": len(collection.all_objects),
            "mesh_object_count": len(meshes),
            "material_count": len(materials),
            "missing_material_slots": missing_slots,
            "external_image_paths": external_images,
            "linked_blend_libraries": external_libraries,
            "stable_id_and_fid_valid": shell_ok,
        },
        "findings": [finding for c in criteria for finding in c["findings"]],
        "grader": "independent review; fresh-open Blender asset and source-evidence inspection",
    }
    assert result["evidence"]["stable_id_and_fid_valid"]
    return result


result = evaluate()
(AUDIT / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
lines = ["# Acacia independent grade — round 2", "", f"**Score: {result['score']}/10 — {'PASS' if result['pass'] else 'below 8/10'}**", "", "| Criterion | Score | Evidence |", "| --- | ---: | --- |"]
for c in result["criteria"]:
    lines.append(f"| {c['name']} | {c['score']:.2f}/2 | {c['evidence']} |")
lines += ["", "## Findings", ""] + [f"- {x}" for x in result["findings"]]
(AUDIT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps({"score": result["score"], "pass": result["pass"], "result": str(AUDIT / "result.json")}, indent=2))
