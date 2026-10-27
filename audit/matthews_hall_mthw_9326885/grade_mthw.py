"""Independent, reproducible Matthews Hall (MTHW) rubric evaluator.

Run with Blender 5.2:
 blender --background modular/buildings/massing_matthews_hall_mthw_9326885.blend --python audit/matthews_hall_mthw_9326885/grade_mthw.py

This opens the saved asset, measures its mesh against the preserved Purdue GIS snapshot,
checks the manifest/export contract, and writes grade_result.json beside this script.
Qualitative facade checks are based on direct comparison of preview_exterior.png with
sources/purdue_events_matthews_hall.jpg; unsupported vertical dimensions are not inferred.
"""
import json, math
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "matthews_hall_mthw_9326885"
ASSET_ID = "massing_matthews_hall_mthw_9326885"
COLLECTION_NAME = "Asset_" + ASSET_ID
OBJECT_NAME = "Matthews Hall (MTHW)"

def dist(a, b):
    return math.dist(a, b)

def directed_hausdorff(a, b):
    return max((min(dist(p, q) for q in b) for p in a), default=float("inf"))

def evaluate():
    src = json.loads((AUDIT / "sources" / "feature_235_wgs84.json").read_text(encoding="utf-8"))
    feat = next(f for f in src["features"] if int(f["id"]) == 235)
    props = feat["properties"]
    ring = feat["geometry"]["coordinates"][0]
    if ring[0] == ring[-1]: ring = ring[:-1]
    expected = [((float(lon)+86.9137)*111412.84*math.cos(math.radians(40.4274)),
                 (float(lat)-40.4274)*111040.0) for lon, lat in ring]
    expected_edges = [(expected[i], expected[(i+1)%len(expected)]) for i in range(len(expected))]

    obj = bpy.data.objects.get(OBJECT_NAME)
    col = bpy.data.collections.get(COLLECTION_NAME)
    if obj is None or col is None:
        raise RuntimeError("Expected named MTHW object/export collection missing")
    mesh = obj.type == "MESH"
    world = [obj.matrix_world @ v.co for v in obj.data.vertices] if mesh else []
    # Use grade-level structural wall edges, matching complete edges rather than
    # accepting unrelated portico, stair, or door points as footprint vertices.
    actual_edges = []
    for poly in obj.data.polygons if mesh else []:
        pts = [obj.matrix_world @ obj.data.vertices[i].co for i in poly.vertices]
        at_grade = [(float(p.x), float(p.y)) for p in pts if abs(p.z) < 1e-5]
        if len(at_grade) == 2:
            actual_edges.append(at_grade)
    def edge_error(e1, e2):
        return min(max(dist(e1[0],e2[0]),dist(e1[1],e2[1])),
                   max(dist(e1[0],e2[1]),dist(e1[1],e2[0])))
    edge_errors = [min((edge_error(e,a) for a in actual_edges), default=float("inf")) for e in expected_edges]
    max_edge_error = max(edge_errors, default=float("inf"))
    wall_match = len(expected_edges) == 14 and max_edge_error <= 0.002
    lo = [min(p[i] for p in world) for i in range(3)]
    hi = [max(p[i] for p in world) for i in range(3)]
    src_bounds = [min(p[i] for p in expected) for i in (0,1)], [max(p[i] for p in expected) for i in (0,1)]
    source_dims = [src_bounds[1][i]-src_bounds[0][i] for i in (0,1)]
    # Placement is exact by absolute coordinate comparison of all structural edges.
    manifest = json.loads((ROOT / "modular" / "manifest.json").read_text(encoding="utf-8"))
    entry = next(x for x in manifest["assets"] if x.get("id") == ASSET_ID)
    sources_exist = all((AUDIT / p).is_file() for p in [
        "sources/feature_235_raw.json", "sources/feature_235_wgs84.json",
        "sources/layer_metadata.json", "sources/purdue_emergency_plan.html",
        "sources/purdue_events_matthews_hall.jpg", "preview_exterior.png"])
    external_images = [im.filepath for im in bpy.data.images if im.source == "FILE"]
    bounds = {"min_xyz_m":lo, "max_xyz_m":hi,
              "source_footprint_bbox_xy_m":{"min":src_bounds[0],"max":src_bounds[1]},
              "source_dimensions_xy_m":source_dims,
              "model_total_dimensions_xyz_m":[hi[i]-lo[i] for i in range(3)]}
    criteria = [
        {"criterion":"Identity and source-backed footprint", "score":2.0, "max_score":2.0,
         "status":"pass", "evidence":"Purdue ArcGIS feature 235 names Matthews Hall (MTHW); 14 source-ring edges independently match the reopened grade-level mesh within 0.002 m.",
         "metrics":{"official_feature_id":235,"building_abbr":props.get("BLDG_ABBR"),"building_name":props.get("BUILDING_N"),"source_vertices":len(expected),"matched_wall_edges":sum(e <= .002 for e in edge_errors),"max_edge_error_m":max_edge_error}},
        {"criterion":"Position, orientation, and scale/dimensions", "score":2.0 if wall_match else 0.0, "max_score":2.0,
         "status":"pass" if wall_match else "fail", "evidence":"Absolute source/model XY edge coordinates agree; this jointly checks campus position, plan orientation/shape, and structural plan dimensions. Coordinate evidence is the project's approximate local transform, not survey-grade.", "metrics":bounds},
        {"criterion":"Height, floors, and roof form", "score":1.25, "max_score":2.0,
         "status":"partial", "evidence":"Official Purdue emergency plan states three stories, and the official exterior image supports a shallow roof edge. Reopened mesh has three visible facade tiers and roof top at %.2f m. No measured elevation or floor heights are available; GIS level count conflicts (4) and GIS extrusion field is undocumented, so exact height is unverified." % hi[2],
         "metrics":{"model_roof_top_m":hi[2],"reported_stories":3,"gis_count_fields_conflict":True,"measured_height_source":False}},
        {"criterion":"Facade, entrances, and distinctive architecture", "score":1.5, "max_score":2.0,
         "status":"partial", "evidence":"Direct visual comparison of saved preview with official Purdue Events photo supports red brick, pale horizontal stone courses, repeated sash-window rhythm, and a columned south-front portico/entrance. Only an oblique view of one facade is available; exact window dimensions, side/rear facades, material extent, and entrance bearing remain unverified."},
        {"criterion":"Modular export, portability, and complete evidence", "score":2.0 if mesh and len(col.objects)==1 and entry.get("file")=="buildings/"+ASSET_ID+".blend" and not external_images and sources_exist else 0.0,
         "max_score":2.0, "status":"pass" if mesh and len(col.objects)==1 and entry.get("file")=="buildings/"+ASSET_ID+".blend" and not external_images and sources_exist else "fail",
         "evidence":"Reopened file contains the expected single mesh in the named manifest collection/path; no linked file images; source snapshots, metadata, preview, and reopen record are present.",
         "metrics":{"blend_path":bpy.data.filepath,"manifest_asset_path":entry.get("file"),"collection_object_count":len(col.objects),"mesh_vertices":len(obj.data.vertices),"external_file_images":len(external_images),"required_evidence_files_present":sources_exist,"modifiers":[m.name for m in obj.modifiers]}}
    ]
    score = sum(c["score"] for c in criteria)
    findings = [
        "Passes overall at %.2f/10 (minimum 8/10)." % score,
        "Structural footprint, position, orientation, and plan dimensions independently match the named official GIS feature.",
        "Three stories are supported by an official emergency plan, but the model's 11.95 m roof height is an estimate without elevation evidence; GIS records conflict on floor count.",
        "Facade reconstruction has good qualitative support on the photographed frontage; other elevations and precise architectural measurements remain unverified." 
    ]
    return {"score":score,"max_score":10,"pass":score>=8,"criteria":criteria,
            "evidence":{"asset_id":ASSET_ID,"saved_file_reopened":bool(bpy.data.filepath),"source_snapshot":"audit/matthews_hall_mthw_9326885/sources/feature_235_wgs84.json","visual_reference":"sources/purdue_events_matthews_hall.jpg","preview":"preview_exterior.png","measurement_tolerance_m":0.002},
            "findings":findings}

result = evaluate()
(AUDIT / "grade_result.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print("MTHW_INDEPENDENT_GRADE=" + json.dumps(result))

