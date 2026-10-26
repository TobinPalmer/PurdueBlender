"""Independent evaluator for Union Club Hotel asset, rubric from AGENT.md.

Run with Blender 4.5 background. The script opens the saved library directly,
checks its GIS base ring against the preserved official FID 663 snapshot, and
writes grade_result.json beside this file. It does not modify the asset.
"""
from __future__ import annotations
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSET_ID = "massing_union_club_hotel_0d22460"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
GIS_SNAPSHOT = HERE / "sources" / "official_gis_fid_663.json"
OUT = HERE / "grade_result.json"
EXPECTED = "Asset_" + ASSET_ID


def proj_xy(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def evaluate():
    # Open the committed candidate asset fresh, independent of the builder scene.
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    collection = bpy.data.collections.get(EXPECTED)
    if not collection:
        raise RuntimeError(f"Missing expected exported collection {EXPECTED}")
    gis = json.loads(GIS_SNAPSHOT.read_text(encoding="utf-8"))
    feat = gis["feature"]
    if int(feat["attributes"]["FID"]) != 663:
        raise RuntimeError("Supplied GIS snapshot does not contain FID 663")
    raw_ring = feat["geometry"]["rings"][0]
    source = [proj_xy(float(lon), float(lat)) for lon, lat in raw_ring]
    if len(source) > 1 and math.dist(source[0], source[-1]) < 0.001:
        source.pop()
    body = bpy.data.objects.get("Union Club Hotel")
    if body is None or body.type != "MESH":
        raise RuntimeError("Expected structural shell object Union Club Hotel")
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_body = body.evaluated_get(depsgraph)
    eval_mesh = eval_body.to_mesh()
    try:
        evaluated = [eval_body.matrix_world @ v.co for v in eval_mesh.vertices]
    finally:
        eval_body.to_mesh_clear()
    # This asset is campus-coordinate massing; the first source-ring-sized block
    # of mesh vertices is the bottom perimeter by construction. Compare geometry
    # coordinates to current preserved official GIS coordinates, with tolerance.
    base_actual = [body.matrix_world @ body.data.vertices[i].co
                   for i in range(min(len(source), len(body.data.vertices)))]
    point_errors = [math.dist((p.x, p.y), q) for p, q in zip(base_actual, source)]
    max_error = max(point_errors) if point_errors else None
    centroid_src = (sum(p[0] for p in source)/len(source), sum(p[1] for p in source)/len(source))
    centroid_mesh = (sum(p.x for p in base_actual)/len(base_actual), sum(p.y for p in base_actual)/len(base_actual)) if base_actual else (None, None)
    centroid_error = math.dist(centroid_src, centroid_mesh) if base_actual else None
    source_bounds = [[min(p[0] for p in source), max(p[0] for p in source)],
                     [min(p[1] for p in source), max(p[1] for p in source)]]
    coords = []
    object_details = []
    for obj in collection.objects:
        if obj.type == "MESH":
            ev = obj.evaluated_get(depsgraph)
            me = ev.to_mesh()
            try:
                world = [ev.matrix_world @ v.co for v in me.vertices]
                coords.extend(world)
                object_details.append({"name": obj.name, "type": "MESH",
                    "vertices_evaluated": len(world), "materials": len(obj.data.materials),
                    "modifiers": [m.name for m in obj.modifiers],
                    "matrix_world": [list(row) for row in obj.matrix_world]})
            finally:
                ev.to_mesh_clear()
        else:
            object_details.append({"name": obj.name, "type": obj.type,
                                   "materials": len(obj.data.materials) if hasattr(obj.data, "materials") else None,
                                   "modifiers": [m.name for m in obj.modifiers]})
    all_portable_images = [im.filepath for im in bpy.data.images
                           if im.source == "FILE" and im.packed_file is None and im.filepath]
    world_bounds = [[min(v.x for v in coords), min(v.y for v in coords), min(v.z for v in coords)],
                    [max(v.x for v in coords), max(v.y for v in coords), max(v.z for v in coords)]]
    metadata = {
        "asset_path": str(ASSET), "asset_id": ASSET_ID,
        "expected_collection": EXPECTED, "collection_found": True,
        "collection_object_count": len(collection.objects),
        "mesh_count": sum(o.type == "MESH" for o in collection.objects),
        "gis_feature": {"FID": feat["attributes"]["FID"],
                        "name": feat["attributes"]["BUILDING_N"],
                        "abbreviation": feat["attributes"]["BLDG_ABBR"],
                        "levels": feat["attributes"]["NUM_LEVELS"],
                        "ring_vertex_count": len(source)},
        "actual_shell_vertex_count": len(body.data.vertices),
        "actual_base_ring_count_compared": len(base_actual),
        "max_base_ring_error_m": max_error,
        "base_centroid_error_m": centroid_error,
        "source_xy_bounds_m": source_bounds,
        "evaluated_asset_bounds_m": world_bounds,
        "evaluated_asset_height_m": world_bounds[1][2] - world_bounds[0][2],
        "unpacked_external_images": all_portable_images,
        "objects": object_details,
        "asset_scene": bpy.context.scene.name,
        "asset_transform_note": "Simple massing remains in campus coordinates; no detailed Placement marker is expected.",
    }

    # Criterion scoring (0-2 each); visual/source judgements are documented below.
    criteria = [
      {"name": "Correct identity and source-backed footprint", "score": 2.0, "max_score": 2.0,
       "status": "verified", "evidence": "Official GIS FID 663 names Purdue Memorial Union Club (PMUC), address 201 N Grant Street; the official campus map separately lists PMU and PMUC. Purdue Events identifies the PMUC property as the Union Club Hotel addition. The candidate shell's 53-point base ring matches the 53 distinct GIS vertices in order; direct evaluation found maximum XY error %.8f m and centroid displacement %.8f m." % (max_error or 0.0, centroid_error or 0.0),
       "limitations": "The project's local lon/lat-to-meter approximation is not a surveyed projection."},
      {"name": "Position, orientation, and scale/dimensions", "score": 1.8, "max_score": 2.0,
       "status": "mostly verified", "evidence": "The complete irregular 53-vertex GIS outline is reproduced at campus coordinates and has the same source ordering/orientation. The evaluated overall XY envelope is %.3f x %.3f m versus the converted source envelope %.3f x %.3f m; the small difference is exterior trim/entry geometry. No arbitrary translation or global scale is apparent." % (world_bounds[1][0]-world_bounds[0][0], world_bounds[1][1]-world_bounds[0][1], source_bounds[0][1]-source_bounds[0][0], source_bounds[1][1]-source_bounds[1][0]),
       "limitations": "The GIS conversion has local-approximation uncertainty; model dimensions outside the base polygon include trim and the portico."},
      {"name": "Evidence-backed height, floors, and roof form", "score": 1.0, "max_score": 2.0,
       "status": "partially verified; roof silhouette unsupported", "evidence": "GIS reports NUM_LEVELS=7 and height-related fields F01-F06, R=63.1, and Extrution=72. The modeled seven floor bands and 21.95 m top are plausible if the undocumented values are feet, but that unit conversion is an estimate. Reopened model bounds place the body/top at about %.2f m. Roof views show an essentially broad flat/capped slab with a small penthouse; the preserved official 80x80 photo thumbnail suggests more varied pitched/gabled roof silhouettes, but is too low resolution for exact roof measurement." % world_bounds[1][2],
       "limitations": "No elevations or unit-documented height source. Roof geometry is not substantiated by the GIS and visibly simplifies the photo-supported roofline; 21.95 m is an estimate."},
      {"name": "Facade, entrances, and distinctive architecture", "score": 0.8, "max_score": 2.0,
       "status": "weakly supported", "evidence": "The model supplies a plausible red-brick palette, repeated punched openings, limestone-colored bands, and a gabled covered entrance. Purdue Events has an official exterior image, but the preserved copy is only 80x80 pixels and does not support window count, spacing, floor-by-floor changes, or exact portico placement. In the renders, nearly every elevation has a highly regular identical window grid and belt course; the entry is tiny relative to the long wing and its location is explicitly inferred by the build script rather than measured from a clear elevation.",
       "limitations": "No facade plans or readable high-resolution, current exterior elevations. Distinctive hotel details and exact entrance/frontage remain largely interpretive."},
      {"name": "Modular export, portability, and complete evidence", "score": 1.7, "max_score": 2.0,
       "status": "mostly verified", "evidence": "Fresh-opened .blend contains the exact stable exported collection %s with %d objects (%d meshes), readable asset metadata, and materials on evaluated meshes. No unpacked external image paths were found. The asset and build script preserve the stable ID/path and the campus-coordinate massing convention. Four renders, a source index/evidence narrative, raw GIS feature snapshot, official map and Purdue source snapshots, and reopen validation are present. The saved renders are consistent with the geometry checked directly." % (EXPECTED, len(collection.objects), sum(o.type == "MESH" for o in collection.objects)),
       "limitations": "No master-link/duplicate-removal review is within this independent asset audit; coordinator must check final integration. Evidence has only one low-resolution exterior image."},
    ]
    score = round(sum(c["score"] for c in criteria), 1)
    findings = [
      "FAIL: total is below the required 8/10 threshold; revise and request a fresh independent grade.",
      "Replace the near-uniform flat top/large simple slab with a roof silhouette supported by higher-resolution exterior imagery or plans; keep unsupported heights explicitly estimated.",
      "Improve facade and entrance differentiation only where exterior source imagery can substantiate it. Seek a readable official/current hotel exterior image or elevation; current preserved image is only 80x80 and the rendered entrance is small and inferred.",
      "The GIS footprint, identity crosswalk, and seven-level field provide strong horizontal/identity support. Do not alter the matched 53-point footprint without new source evidence.",
    ]
    return {"score": score, "max_score": 10, "pass_threshold": 8.0,
            "passed": score >= 8.0, "criteria": criteria,
            "evidence": {"direct_saved_asset_inspection": metadata,
                         "rendered_views_inspected": [
                           "renders/east_oblique.png", "renders/northwest_oblique.png",
                           "renders/south_oblique.png", "renders/top.png"],
                         "source_material_inspected": [
                           "sources/official_gis_fid_663.json",
                           "sources/official_purdue_campus_map.pdf",
                           "sources/official_purdue_events_pmuc.html",
                           "sources/official_event_listing_photo.jpg (80x80)",
                           "sources/official_purdue_2018_hotel_history.html",
                           "sources/official_purdue_union_history_podcast.html",
                           "source_evidence.md", "reopen_validation.json"]},
            "findings": findings}


result = evaluate()
OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({"grade_result": str(OUT), "score": result["score"],
                  "passed": result["passed"],
                  "max_base_ring_error_m": result["evidence"]["direct_saved_asset_inspection"]["max_base_ring_error_m"]}, indent=2))
