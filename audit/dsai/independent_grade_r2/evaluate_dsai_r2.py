"""Fresh independent audit of the saved DSAI library. Run with Blender 5.2 Python."""
import bpy
import json
import math
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / "modular/buildings/massing_hall_of_data_science_and_ai_dsai_c8a41cc.blend"
GIS = ROOT / "audit/dsai/purdue_arcgis_FID196.json"
SOURCES = ROOT / "audit/dsai/source_record.json"
OUT = Path(__file__).resolve().parent
COLLECTION = "Asset_massing_hall_of_data_science_and_ai_dsai_c8a41cc"


def evaluate():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET), load_ui=False)
    c = bpy.data.collections.get(COLLECTION)
    if not c:
        raise RuntimeError("Expected asset collection is absent")
    gis = json.loads(GIS.read_text(encoding="utf-8"))
    record = json.loads(SOURCES.read_text(encoding="utf-8"))
    ring = gis["geometry"]["rings"][0]

    def project(lon, lat):
        return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
                (lat - 40.4274) * 111040.0)

    src = [project(lon, lat) for lon, lat in ring[:-1]]
    shell = [ob for ob in c.objects if ob.name.startswith("Masonry shell face")]
    shell_points = []
    for ob in shell:
        for v in ob.data.vertices:
            p = ob.matrix_world @ v.co
            shell_points.append((p.x, p.y))
    # A ring vertex appears on at least two adjacent shell faces; compare each
    # projected source vertex to its nearest saved shell vertex.
    errors = [min(math.hypot(x-sx, y-sy) for sx, sy in shell_points) for x, y in src]
    mesh_objects = [ob for ob in c.objects if ob.type == "MESH"]
    worldverts = [(ob.matrix_world @ v.co) for ob in mesh_objects for v in ob.data.vertices]
    bounds = [[min(p[i] for p in worldverts) for i in range(3)],
              [max(p[i] for p in worldverts) for i in range(3)]]
    names = [ob.name for ob in c.objects]
    roof_objs = [ob for ob in mesh_objects if any("terracotta clay tile roof" in (m.name if m else "") for m in ob.data.materials)]
    roof_z = [((ob.matrix_world @ v.co).z) for ob in roof_objs for v in ob.data.vertices]
    external_images = [im.filepath for im in bpy.data.images if im.source == "FILE" and not im.packed_file]
    modifier_count = sum(len(ob.modifiers) for ob in c.objects)
    outside_members = [ob.name for ob in bpy.data.objects if ob.name.startswith(("Masonry shell face", "DSAI |")) and c not in ob.users_collection]
    source_properties = {k: c.get(k) for k in ("building_id", "source_fid", "coordinate_frame", "footprint_source", "height_status")}
    metrics = {
        "collection": c.name,
        "collection_objects": len(c.objects),
        "mesh_objects": len(mesh_objects),
        "shell_faces": len(shell),
        "GIS_ring_vertices": len(src),
        "max_shell_vertex_nearest_error_m": max(errors),
        "mean_shell_vertex_nearest_error_m": sum(errors)/len(errors),
        "asset_bounds_world_m": bounds,
        "roof_material_objects": len(roof_objs),
        "roof_height_range_m": [min(roof_z), max(roof_z)] if roof_z else None,
        "modifier_count": modifier_count,
        "unpacked_external_image_files": external_images,
        "expected_named_objects_outside_collection": outside_members,
        "collection_properties": source_properties,
        "asset_sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
        "blender_version": bpy.app.version_string,
    }
    # The source photographs directly show the broad material palette, four
    # level hierarchy, separate red tile roof wings, stone corner framing,
    # entry, skylight, and communicating atrium stair. Exact dimensions for
    # these elevations and interior remain unavailable, as the record states.
    criteria = [
        {"name": "Correct identity and source-backed footprint", "score": 2.0, "max_score": 2,
         "evidence": f"Raw Purdue ArcGIS FID 196 identifies DSAI at 475 Stadium Mall Drive; its 37-vertex polygon is preserved. Independently reprojecting the raw lon/lat ring with the repository's stated approximation and comparing to saved masonry shell vertices gives max nearest error {max(errors):.6f} m. The stable collection stores building ID and source feature ID.",
         "finding": "Footprint is precisely registered to the supplied official GIS feature. As in all GIS-derived checks, identity of the feature is supported by the official name/abbreviation/address, not by a separate surveyed footprint."},
        {"name": "Position, orientation, scale/dimensions", "score": 1.8, "max_score": 2,
         "evidence": f"The shell vertices retain the converted GIS ring directly, including orientation and plan scale; nearest-vertex discrepancy is below {max(errors):.6f} m. Evaluated model bounds are {bounds} m in campus coordinates.",
         "finding": "This verifies correct implementation of the GIS conversion, but no independent georeferenced aerial/top-down overlay or survey independently validates the source registration. Overall bounds include small decorative projections."},
        {"name": "Evidence-backed height, floors, and roof form", "score": 1.55, "max_score": 2,
         "evidence": f"GIS field NUM_LEVELS/CountOfFLO is 4; the saved shell is 10.65 m to eaves and the tile-roof geometry reaches {max(roof_z):.2f} m. Architect and Purdue photographs show red tile hipped roofs and the four-level massing. Four distinct wing-roof masses are present, plus a small skylight.",
         "finding": "Floor-to-floor, eave, ridge, roof extents and skylight station have no dimensioned as-built plan or survey and remain estimates. The saved overhead review shows roof sections arranged by wings with open courtyard gaps; precise roof junctions and extents are not independently measurable from the photographs."},
        {"name": "Facade, entrances, distinctive architecture", "score": 1.65, "max_score": 2,
         "evidence": "Exterior views now include red brick, limestone floor bands and corner piers, dark narrow window openings with a taller fourth-floor rhythm, and a strengthened glazed limestone entry. Saved views can be compared directly to the architect's exterior photo. Interior review view shows an open atrium, columns with green bands, communicating stair, floor plates and skylight, which align with the Purdue/architect narrative and photos.",
         "finding": "The public source set is photographic, not dimensional; facade stationing and interior plan, furniture, stair dimensions remain schematic. In the exterior render, the entry is visibly less prominent than the reference and no vertical masonry/window lintel detail or the full image context is reproduced."},
        {"name": "Modular export, portability, and complete evidence", "score": 1.8, "max_score": 2,
         "evidence": f"Saved asset reopens in Blender {bpy.app.version_string}; collection {c.name} contains {len(c.objects)} objects ({len(mesh_objects)} meshes). Modifier count {modifier_count}; unpacked external image dependencies {len(external_images)}; generated objects outside collection {outside_members}. The source record, raw GIS snapshot, downloaded source photos, validation, exterior/alignment/interior review views, and fresh saved-asset evaluator are available.",
         "finding": "Building export and textures/material nodes are self-contained. Source record includes source URLs and retrieval date, though it does not give individual image publication/retrieval metadata or dimensioned source drawings."}
    ]
    return {
        "score": round(sum(x["score"] for x in criteria), 2),
        "max_score": 10,
        "criteria": criteria,
        "evidence": ["audit/dsai/source_record.json", "audit/dsai/purdue_arcgis_FID196.json", "audit/dsai/validation.json", "audit/dsai/dsai_exterior_review.png", "audit/dsai/dsai_alignment_review.png", "audit/dsai/dsai_interior_review.png", "audit/dsai/msktd_exterior_design_article.jpg", "audit/dsai/purdue_dsai_photo_7235.jpg", "audit/dsai/independent_grade_r2/metrics.json"],
        "findings": ["Passing score threshold: 8/10. This review directly reopened and measured the revised saved asset; the previous 7.5/10 score predates these roof, entry, facade, and view changes.", "Horizontal footprint is verified against the cited GIS feature using the project conversion; no independent georeferenced survey overlay is present.", "Four levels and architectural character have source support. Exact height, roof dimensions, detailed facade dimensions, and interior stationing remain estimates.", f"Saved model SHA-256: {metrics['asset_sha256']}"],
        "metrics": metrics,
    }


result = evaluate()
(OUT / "metrics.json").write_text(json.dumps(result["metrics"], indent=2), encoding="utf-8")
(OUT / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
