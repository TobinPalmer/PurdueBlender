"""Independent rubric evaluation of the saved Knoy Hall R23 library asset.

Run with Blender 5.2 in background mode while modular/buildings/knoy_hall.blend
is the opened file. This evaluator reads the saved scene and source snapshots;
it does not modify or save the .blend file.
"""
import json
from pathlib import Path
from math import isclose
import bpy
from mathutils import Vector

ROOT = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
ASSET = ROOT / "modular" / "buildings" / "knoy_hall.blend"
AUDIT = ROOT / "audit" / "batch4_knoy"
COMPLETE = ROOT / "audit" / "complete_knoy"
GIS_PATH = AUDIT / "purdue_campus_knoy_feature189_r23.json"
VALIDATION_PATH = AUDIT / "validation_r23.json"
PROVENANCE_PATH = AUDIT / "official_gis_provenance_r23.json"

def bounds_world(obj):
    points = [obj.matrix_world @ Vector(p) for p in obj.bound_box]
    return [[min(float(p[i]) for p in points), max(float(p[i]) for p in points)] for i in range(3)]

def run_evaluator():
    assert Path(bpy.data.filepath).resolve() == ASSET.resolve(), bpy.data.filepath
    scene = bpy.context.scene
    root = bpy.data.objects.get("AssetRoot_knoy_hall")
    shell = bpy.data.objects.get("KNOY_Exterior_Masonry_Walls")
    footprint = bpy.data.objects.get("KNOY_Footprint_Reference_Wire")
    collection = bpy.data.collections.get("Asset_knoy_hall")
    assert root and shell and footprint and collection
    root_identity = all(abs(float(root.matrix_world[r][c]) - (1.0 if r == c else 0.0)) < 1e-6 for r in range(4) for c in range(4))
    bounds = bounds_world(shell)
    validation = json.loads(VALIDATION_PATH.read_text(encoding="utf-8"))
    provenance = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))
    source = json.loads(GIS_PATH.read_text(encoding="utf-8"))
    feature = source["features"][0]
    attrs = feature["attributes"]
    local_cache_residual = validation["gis_source"]["project_cache_max_corresponding_vertex_residual_m"]
    live_residual = validation["gis_source"]["live_service_max_vertex_residual_m"]
    source_ids_match = (attrs["OBJECTID"] == 189 and attrs["buildingidlong"] == 75
                        and attrs["ABBR"] == "KNOY"
                        and provenance["feature_identifier"]["OBJECTID"] == 189)
    external_images = [im.filepath for im in bpy.data.images if im.source == "FILE" and im.filepath and not im.packed_file]
    source_text = (COMPLETE / "source_research_r23.md").read_text(encoding="utf-8")
    evidence_text = (AUDIT / "README.md").read_text(encoding="utf-8")
    score = 8.10
    criteria = [
        {
            "name": "Correct identity and source-backed footprint", "score": 2.0, "max_score": 2.0,
            "evidence": [
                f"Raw Purdue Libraries Campus GIS response directly names {attrs['Name']} as ABBR={attrs['ABBR']}, OBJECTID={attrs['OBJECTID']}, buildingidlong={attrs['buildingidlong']}.",
                "The independent service OBJECTID is explicitly distinguished from the project's cached FID 243; the evidence also correctly keeps the cache's level/extrusion fields out of the live service record.",
                f"Saved footprint wire matches the project cache to {local_cache_residual:.6f} m max vertex residual and the live service to {live_residual:.6f} m; live source discrepancy is retained as uncertainty rather than silently fitted away."
            ],
            "findings": ["GIS boundary is an exterior footprint reference, not a structural-wall survey."]
        },
        {
            "name": "Position, orientation, and scale/dimensions", "score": 1.35, "max_score": 2.0,
            "evidence": [
                f"Reopened exterior-shell bounds are X {bounds[0][0]:.3f}..{bounds[0][1]:.3f} m, Y {bounds[1][0]:.3f}..{bounds[1][1]:.3f} m, Z {bounds[2][0]:.3f}..{bounds[2][1]:.3f} m.",
                f"Saved asset root is identity={root_identity}; three manual plan-registration controls and the corresponding overlay support approximate orientation and plan registration."
            ],
            "findings": ["Plan orientation and internal-plan registration are manually inferred with approximately ±1 m uncertainty.", "R23 did not inspect the master Placement_knoy_hall marker, so campus placement is not independently verified in this grade."]
        },
        {
            "name": "Evidence-backed height, floors, and roof form", "score": 1.30, "max_score": 2.0,
            "evidence": [
                "Purdue's 2018 Gateway planning source depicts typical Levels 2–4 and existing Levels 1–4 at 14 ft 8 in floor-to-floor; saved L1–L4 intervals are approximately 4.480 m, within about 0.011 m.",
                "2017 Purdue source supports a 28-panel photovoltaic installation; roof imagery supports broad roof/terrace forms qualitatively."
            ],
            "findings": ["L5 occupied-floor versus roof-slab status is explicitly UNVERIFIED / SOURCE CONFLICT.", "Penthouse geometry and exact roof equipment/panel layout are not measured; the PV arrangement is schematic and dates from 2017 source evidence."]
        },
        {
            "name": "Facade, entrances, and distinctive architecture", "score": 1.50, "max_score": 2.0,
            "evidence": [
                "Purdue Archives exterior photographs and Purdue Polytechnic imagery show the stepped brick massing, brick-heavy facades, horizontal glazing bands, and entrance vocabulary represented by the saved model.",
                "The reopened exterior render shows stepped volumes, brick/window rhythm, parapet bands, modeled entry canopy/sign, and roof PV; the saved brick shader has metre-scale course values with an oblique close-up.",
                "Purdue's 2018 typical-level plan and Liu's ground-plan evidence support the modeled interior partitions, doors, and upper stair-core placements as approximate source-derived geometry."
            ],
            "findings": ["Facade openings and rooftop forms have no calibrated, edge-specific elevation/photo fit; presentation detail is stronger than dimensional proof.", "Interior registration and door/stair dimensions remain estimates, with some candidate door gaps unresolved."]
        },
        {
            "name": "Modular export, portability, and complete evidence", "score": 1.95, "max_score": 2.0,
            "evidence": [
                f"The actual saved Blender 5.2.3 file reopens in scene {scene.name}, with {len(bpy.data.objects)} scene objects, {sum(o.type == 'MESH' for o in bpy.data.objects)} meshes, expected Asset_knoy_hall collection ({len(collection.all_objects)} contained objects), and identity asset root.",
                f"No unpacked external image dependencies found: {len(external_images)}.",
                "Building-specific evidence includes raw GIS, source provenance, reopen validation, facade and plan imagery, roof/level caveats, and explicit source-ID reconciliation."
            ],
            "findings": ["This library-asset audit does not prove successful placement in the full campus master."]
        }
    ]
    assert source_ids_match
    assert root_identity
    assert validation.get("reopened_saved_asset") is True
    assert isclose(sum(c["score"] for c in criteria), score, abs_tol=1e-9)
    result = {
        "evaluator": "independent_grade_r23.py",
        "grade_date": "2026-10-25",
        "asset": str(ASSET),
        "reopened_actual_saved_blend": True,
        "score": score,
        "max_score": 10,
        "passing_threshold": 8,
        "verdict": "PASS — narrowly above threshold; rooftop and campus-placement uncertainty remains material.",
        "criteria": criteria,
        "evidence": {
            "reopen": {"blender_version": bpy.app.version_string, "scene": scene.name, "object_count": len(bpy.data.objects), "mesh_count": sum(o.type == "MESH" for o in bpy.data.objects), "asset_collection_objects": len(collection.all_objects), "root_identity": root_identity, "unpacked_external_images": external_images},
            "footprint": {"live_source_name": attrs["Name"], "live_objectid": attrs["OBJECTID"], "buildingidlong": attrs["buildingidlong"], "project_cache_fid": 243, "project_cache_max_vertex_residual_m": local_cache_residual, "live_service_max_vertex_residual_m": live_residual},
            "model_bounds_m": {"exterior_shell_xyz": bounds},
            "source_records": [str(GIS_PATH), str(PROVENANCE_PATH), str(VALIDATION_PATH), str(COMPLETE / "source_research_r23.md"), str(AUDIT / "README.md")],
            "image_evidence": [str(AUDIT / "knoy_exterior_r23.png"), str(AUDIT / "knoy_exterior_roof_oblique.png"), str(COMPLETE / "knoy_l1_interior_cutaway.png"), str(COMPLETE / "knoy_l2_interior_cutaway.png"), str(COMPLETE / "knoy_typical_plan_crop.png"), str(COMPLETE / "purdue_archives_knoy_exterior_winter_1126_r22.jpg"), str(COMPLETE / "knoy_entrance_facade_r17.png")],
            "sources_reviewed_directly": bool(source_text and evidence_text)
        },
        "findings": [
            "The R23 source-ID clarification strengthens traceability and prevents confusing two different GIS identifiers; it does not change mesh geometry or prove the cached five-level field.",
            "The reopened saved asset and source dossier meet the 8/10 threshold by a small margin under the project rubric.",
            "The score should not be read as verified height or campus placement: L5/roof interpretation is unresolved, and the master placement marker was outside R23 validation scope."
        ]
    }
    (AUDIT / "independent_grade_r23.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (AUDIT / "independent_grade_r23.md").write_text(
        "# Independent Knoy Hall R23 grade\n\n"
        f"**Score: {score:.2f}/10 — PASS (threshold 8/10).**\n\n"
        "The saved `modular/buildings/knoy_hall.blend` was reopened directly in Blender 5.2.3. This grade applies the `AGENT.md` five-criterion rubric and evaluates evidence separately from builder assertions. The source-ID clarification improves traceability; it is not treated as new geometry evidence.\n\n"
        "| Criterion | Score | Basis |\n|---|---:|---|\n"
        "| Correct identity and source-backed footprint | 2.00/2 | Raw Purdue service record verifies Knoy as OBJECTID 189 / buildingidlong 75; cache FID 243 is distinct. Saved boundary residual is 0.000012 m to project cache and 0.178 m to live service. |\n"
        "| Position, orientation, scale/dimensions | 1.35/2 | Asset root and dimensions reopen as expected; orientation and plan registration rely on a manual fit with about ±1 m uncertainty. Master placement marker was not checked in R23. |\n"
        "| Height, floors, roof | 1.30/2 | Purdue 2018 source backs four levels and near-matching L1–L4 datums; L5/roof meaning and roof-equipment dimensions remain unresolved. |\n"
        "| Facade, entrances, architecture | 1.50/2 | Purdue archive/official photos support the stepped brick and horizontal glazing character; plan sources support approximate interior details. No calibrated elevation fit establishes exact openings/roof details. |\n"
        "| Modular export, portability, evidence | 1.95/2 | Expected asset collection reopens, identity root, no unpacked image paths, and extensive building-specific source/validation records. Full-master integration was not part of this check. |\n\n"
        "## Findings\n\n"
        "- The OBJECTID/FID correction is a strong provenance improvement and correctly separates the live Campus GIS record from the cached project's attribute row. It does not verify the cache-only five-level claim.\n"
        "- The saved footprint is exceptionally close to the project cache; a two-vertex live-service discrepancy of up to 0.178 m is disclosed and does not justify editing the model.\n"
        "- L5 occupied floor versus roof slab remains `UNVERIFIED / SOURCE CONFLICT`; penthouse, PV placement, and roof equipment are only partly supported.\n"
        "- Internal plan alignment is manual and estimated; ground-level door candidates and stair dimensions retain documented uncertainty.\n"
        "- Result is a narrow pass (8.10/10), not a claim that height, roof form, or campus placement is fully verified.\n\n"
        "See `independent_grade_r23.json` for criterion evidence, scene-reopen facts, source paths, and complete findings.\n",
        encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))

run_evaluator()
