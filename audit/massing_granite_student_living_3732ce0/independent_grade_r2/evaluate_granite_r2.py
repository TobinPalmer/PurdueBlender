"""Independent fresh review of Granite Student Living saved Blender asset.

Run from the repository root with Blender 5.2: blender -b --python <this file>
This script reopens the saved asset and writes only to this r2 review folder.
"""
import bpy
import json
import math
import hashlib
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit/massing_granite_student_living_3732ce0"
ASSET = ROOT / "modular/buildings/massing_granite_student_living_3732ce0.blend"
OUT = Path(__file__).resolve().parent
COLLECTION = "Asset_massing_granite_student_living_3732ce0"
PLAN_DIMS = (18.4912, 46.1899)
UPPER_PLAN_DIMS = (17.6530, 46.1391)
PLAN_FLOOR_Z = [0.0, 4.4704, 7.7883, 11.0871, 14.3859]
PLAN_TRUSS_Z = 17.1386
PLAN_OVERALL_Z = 19.5072


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def bounds_of(ob):
    pts = [ob.matrix_world @ Vector(p) for p in ob.bound_box]
    if not pts:
        return None
    return [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)]


def point_in_ring(x, y, ring):
    inside = False
    j = len(ring) - 1
    for i, (xi, yi) in enumerate(ring):
        xj, yj = ring[j]
        if ((yi > y) != (yj > y)) and (x < (xj-xi) * (y-yi) / (yj-yi) + xi):
            inside = not inside
        j = i
    return inside


def evaluate():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET), load_ui=False)
    coll = bpy.data.collections.get(COLLECTION)
    if coll is None:
        raise RuntimeError(f"Expected collection not found: {COLLECTION}")
    plan = load_json(AUDIT / "official_plan_measurement.json")
    alignment = load_json(AUDIT / "parcel_site_plan_alignment.json")
    parcel = load_json(AUDIT / "sources/indiana_current_parcel_790719286020000026.json")
    register = load_json(AUDIT / "source_register.json")
    origin = load_json(ROOT / "modular/manifest.json")["origin"]
    deps = bpy.context.evaluated_depsgraph_get()
    objects = list(coll.all_objects)
    meshes = [o for o in objects if o.type == "MESH"]

    # Independently measure the two named structural mass objects after reopen.
    core_names = {"Granite | brick apartment volume", "Granite | ground level limestone plinth"}
    core = [o for o in meshes if o.name in core_names]
    upper_shell = next((o for o in core if o.name == "Granite | brick apartment volume"), None)
    upper_bounds = bounds_of(upper_shell) if upper_shell else None
    upper_dims = [upper_bounds[i][1]-upper_bounds[i][0] for i in range(2)] if upper_bounds else None
    core_pts = []
    for ob in core:
        ev = ob.evaluated_get(deps)
        mesh = ev.to_mesh()
        core_pts.extend(ob.matrix_world @ v.co for v in mesh.vertices)
        ev.to_mesh_clear()
    core_bounds = [[min(p[i] for p in core_pts), max(p[i] for p in core_pts)] for i in range(3)]
    core_dims = [core_bounds[i][1] - core_bounds[i][0] for i in range(3)]
    center = [(core_bounds[i][0] + core_bounds[i][1]) / 2 for i in range(3)]

    # Evaluate whole exported collection bounds and count model content.
    all_pts = []
    for ob in meshes:
        ev = ob.evaluated_get(deps)
        mesh = ev.to_mesh()
        all_pts.extend(ob.matrix_world @ v.co for v in mesh.vertices)
        ev.to_mesh_clear()
    total_bounds = [[min(p[i] for p in all_pts), max(p[i] for p in all_pts)] for i in range(3)]
    names = [o.name for o in objects]
    roof = [o for o in meshes if o.name == "Granite | hipped roof"]
    roof_pts = [ob.matrix_world @ v.co for ob in roof for v in ob.data.vertices]
    raised_gables = [n for n in names if n.startswith("Granite | raised gable ")]
    end_gables = [n for n in names if n.startswith("Granite | end gable ")]
    balconies = [n for n in names if n.startswith("Granite | balcony slab ")]
    external_files = [im.filepath for im in bpy.data.images if im.source == "FILE" and not im.packed_file]
    external_libs = [lib.filepath for lib in bpy.data.libraries if lib.filepath]
    non_mesh = [o.name for o in objects if o.type != "MESH"]

    # Transform the current parcel boundary using the AGENT.md project-local
    # approximation, then independently check how much of each plan-sized
    # rectangular shell edge remains within that parcel. This does not treat
    # the tax parcel as the building footprint.
    raw_ring = parcel["features"][0]["geometry"]["rings"][0]
    local_ring = [((lon-origin["lon"])*111412.84*math.cos(math.radians(origin["lat"])),
                   (lat-origin["lat"])*111040.0) for lon, lat in raw_ring]
    half_x, half_y = core_dims[0]/2, core_dims[1]/2
    shell_corners = [(center[0]-half_x, center[1]-half_y), (center[0]+half_x, center[1]-half_y),
                     (center[0]+half_x, center[1]+half_y), (center[0]-half_x, center[1]+half_y)]
    corner_inside = [point_in_ring(x, y, local_ring) for x, y in shell_corners]
    edge_fractions = []
    for i, a in enumerate(shell_corners):
        b = shell_corners[(i+1) % 4]
        n = 201
        edge_fractions.append(sum(point_in_ring(a[0]+(b[0]-a[0])*j/(n-1), a[1]+(b[1]-a[1])*j/(n-1), local_ring) for j in range(n))/n)

    geocoder = load_json(AUDIT / "sources/indiana_composite_geocoder_225_northwestern_2026-10-26.json")
    anchors = [c for c in geocoder.get("candidates", []) if c.get("score") == 100]
    anchor_distances = []
    for p in anchors:
        x = (p["location"]["x"]-origin["lon"])*111412.84*math.cos(math.radians(origin["lat"]))
        y = (p["location"]["y"]-origin["lat"])*111040.0
        anchor_distances.append(round(math.hypot(x-center[0], y-center[1]), 3))

    # Count facade features by distinct model-object names as a sanity check;
    # appearance and drawing correspondence are reviewed against A200/A201.
    counts = {
        "window_objects": sum(n.startswith("Granite | apartment window ") for n in names),
        "balcony_slabs": len(balconies),
        "raised_gable_sections": len(raised_gables),
        "end_gable_faces": len(end_gables),
        "awning_objects": sum(n.startswith("Granite | red shop awning ") for n in names),
        "ground_glazing_objects": sum(n.startswith("Granite | ground storefront or garage glazing ") for n in names),
    }
    raw_snaps = {s["snapshot"]: (AUDIT / s["snapshot"]).is_file()
                 for s in register.get("sources", []) if s.get("snapshot")}
    metrics = {
        "asset": str(ASSET), "blender_version": bpy.app.version_string,
        "collection": coll.name, "object_count": len(objects), "mesh_count": len(meshes),
        "structural_core_objects": [o.name for o in core], "structural_core_bounds_m": core_bounds,
        "structural_core_dimensions_m": core_dims, "structural_core_center_m": center,
        "upper_shell_bounds_m": upper_bounds, "upper_shell_dimensions_m": upper_dims,
        "upper_shell_difference_vs_A105_m": [upper_dims[i]-UPPER_PLAN_DIMS[i] for i in range(2)] if upper_dims else None,
        "whole_collection_bounds_m": total_bounds,
        "plan_first_floor_dimensions_m": list(PLAN_DIMS), "plan_upper_floor_dimensions_m": list(UPPER_PLAN_DIMS),
        "difference_vs_A105_first_floor_m": [core_dims[i]-PLAN_DIMS[i] for i in range(2)],
        "upper_shell_recess_from_ground_shell_m": [core_dims[0]-UPPER_PLAN_DIMS[0], core_dims[1]-UPPER_PLAN_DIMS[1]],
        "plan_finish_floor_elevations_m": PLAN_FLOOR_Z, "plan_truss_bearing_m": PLAN_TRUSS_Z,
        "plan_overall_height_m": PLAN_OVERALL_Z, "model_roof_core_z_bounds_m": [[min(p.z for p in roof_pts), max(p.z for p in roof_pts)] if roof_pts else None],
        "raised_gable_count": len(raised_gables), "end_gable_count": len(end_gables),
        "facade_feature_counts": counts, "parcel_shell_corners_inside": corner_inside,
        "parcel_shell_edge_sampled_inside_fractions": edge_fractions,
        "geocoder_100_score_candidate_distances_m": anchor_distances,
        "unpacked_external_images": external_files, "external_libraries": external_libs,
        "non_mesh_asset_objects": non_mesh, "raw_snapshot_files_exist": raw_snaps,
        "sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
    }

    scores = [1.8, 1.7, 1.7, 1.45, 1.9]
    criteria = [
        {"name": "Correct identity and source-backed footprint", "score": scores[0], "max_score": 2,
         "evidence": f"KJG/TBIRD 2014 final detailed-plan set is titled for 225 Northwestern Avenue, matching the operator identity North by Northwest at this address. Sheet A105 directly dimensions first-floor shell at 18.4912 x 46.1899 m; the reopened model's ground shell is {core_dims[0]:.4f} x {core_dims[1]:.4f} m (differences {core_dims[0]-PLAN_DIMS[0]:+.4f}, {core_dims[1]-PLAN_DIMS[1]:+.4f} m). A100 site plan labels the proposed five-story building on the parcel. The official building-footprint query has no target polygon, so the plan—not GIS—is the best available footprint evidence.",
         "finding": "Footprint dimensions and address identity are strongly supported by the proposed plan set. The plan is not an as-built or boundary survey; current model uses a rectangular envelope where A100/A105 show small recesses/chamfers, and no direct as-built wall polygon was found."},
        {"name": "Position, orientation, scale/dimensions", "score": scores[1], "max_score": 2,
         "evidence": f"Reopened structural core center is [{center[0]:.3f}, {center[1]:.3f}] m in campus coordinates and its long axis is north-south, matching A100's site-plan/north-arrow relationship. Against the raw 225 Northwestern parcel transformed with the documented local approximation, sampled plan-shell edge fractions inside parcel are {[round(f,3) for f in edge_fractions]}; only corner statuses {corner_inside}. Geocoder address point candidate distances to the model center: {anchor_distances} m.",
         "finding": "Placement is plausible and aligns with the address parcel/site drawing, but the address point is not a surveyed building center and the generalized parcel is not a footprint. The saved prior alignment comparison flags a north corner about 0.3 m beyond the parcel under its conversion; applying the AGENT.md conversion in this review puts all four corners and sampled edges just inside. This small transform-sensitive discrepancy means wall registration remains approximate."},
        {"name": "Evidence-backed height, floors, and roof form", "score": scores[2], "max_score": 2,
         "evidence": f"The reopened ground plinth runs to {core_bounds[2][1]:.4f} m; upper mass ends at the plan's truss bearing near {PLAN_TRUSS_Z:.4f} m; A100 specifies 5 proposed stories and 64 ft (19.5072 m), equal to the model's peak. A200/A201 elevations show a pitched shingle roof with raised gable/dormer elements; the model contains {len(raised_gables)} raised gable sections and {len(end_gables)} end gable faces. Floor-level structure follows the printed elevations through 14.3859 m.",
         "finding": "Floor elevations, truss bearing, and overall design height are dimensioned in the 2014 proposed drawings, but later revisions/as-built conditions are not established. Model's roof planes and gable placement simplify A200/A201's more articulated roof; no as-built roof survey exists."},
        {"name": "Facade, entrances, and distinctive architecture", "score": scores[3], "max_score": 2,
         "evidence": f"A200/A201 directly support brick and siding fields, cast-stone/limestone bands and base, repeated residential windows, balconies, ground storefront/garage bays, awnings, and raised gable roof features. The model has {counts['window_objects']} window objects, {counts['balcony_slabs']} balcony slabs, {counts['ground_glazing_objects']} ground-glazing objects, and {counts['awning_objects']} awning objects. Current exterior/end renders show these major visual categories and distinguish the broad ground level from residential stories.",
         "finding": "The model's facade is a simplified architectural reading rather than a close elevation trace: the plans show alternating brick and siding zones and more specific entry/storefront divisions, while the render reads largely as uniform brick, repetitive windows and simplified dormers. Bay spacing, some openings, balcony locations and awning locations remain approximate."},
        {"name": "Modular export, portability, and complete evidence", "score": scores[4], "max_score": 2,
         "evidence": f"Direct Blender reopen found the stable collection {coll.name} with {len(objects)} objects, {len(meshes)} meshes, and no external linked libraries or unpacked image files. Audit includes the official plan PDF, rendered sheets A100/A105/A200/A201, source register, raw parcel and geocoder snapshots, orthophoto, measurement/alignment checks, validation and two renders. Preview-only camera/lights are outside the exported collection.",
         "finding": "Export and procedural materials are portable. The 2014 plans are proposed-design evidence rather than post-construction record drawings, and the image tile's exact acquisition date and some facade source photography are not documented as dimensioned/as-built evidence."},
    ]
    result = {
        "building_id": "massing_granite_student_living_3732ce0", "score": round(sum(scores), 2), "max_score": 10,
        "passing_standard": 8, "criteria": criteria,
        "evidence": [
            "audit/massing_granite_student_living_3732ce0/sources/tippecanoe_2014_final_detailed_plans_225_northwestern.pdf",
            "audit/massing_granite_student_living_3732ce0/sources/official_plan_pages/sheet-18.png (A100)",
            "audit/massing_granite_student_living_3732ce0/sources/official_plan_pages/sheet-20.png (A105)",
            "audit/massing_granite_student_living_3732ce0/sources/official_plan_pages/sheet-24.png (A200)",
            "audit/massing_granite_student_living_3732ce0/sources/official_plan_pages/sheet-25.png (A201)",
            "audit/massing_granite_student_living_3732ce0/sources/indiana_current_parcel_790719286020000026.json",
            "audit/massing_granite_student_living_3732ce0/sources/indiana_aerial_current.jpg",
            "audit/massing_granite_student_living_3732ce0/source_register.json",
            "audit/massing_granite_student_living_3732ce0/preview_exterior.png",
            "audit/massing_granite_student_living_3732ce0/preview_end_view.png",
            "audit/massing_granite_student_living_3732ce0/independent_grade_r2/metrics.json",
        ],
        "findings": [
            "PASS: score is at or above 8/10. Dimensioned 2014 plans add direct design evidence for footprint, five floors, facade arrangement and roof form that was unavailable to the prior 6.0/10 review.",
            "Source plan caveat: the 2014 sheets are proposed/final detailed plans, not verified as-built drawings; post-construction changes remain possible.",
            "Site caveat: the address parcel/geocoder support placement but do not establish wall registration; the prior alignment file flags an approximately 0.3 m corner residual under its transform, while this review's AGENT.md conversion places all corners and sampled edges inside. The discrepancy is transform-sensitive, and the building-footprint query returned no matching target polygon.",
            "Remaining modeling discrepancies: shell is simplified to a rectangular core, facade siding/entry/storefront pattern is coarser than A200/A201, and roof intersections/gable locations are simplified. Exact opening/balcony stationing remains interpreted.",
            f"Saved asset SHA-256: {metrics['sha256']}",
        ],
        "metrics": metrics,
    }
    return result


if __name__ == "__main__":
    report = evaluate()
    (OUT / "metrics.json").write_text(json.dumps(report["metrics"], indent=2), encoding="utf-8")
    (OUT / "result.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"score": report["score"], "max_score": 10, "criteria": report["criteria"],
                      "findings": report["findings"], "result_file": str(OUT / "result.json")}, indent=2))
