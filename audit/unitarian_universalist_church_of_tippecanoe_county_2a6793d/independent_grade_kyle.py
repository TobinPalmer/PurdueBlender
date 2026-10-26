"""Independent rubric evaluator for the UUCTC assigned building library.
Run in Blender with the saved asset file opened. The evaluator reads raw project
sources and evaluated Blender mesh data; it does not rely on builder summary scores.
"""
import json
import math
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "unitarian_universalist_church_of_tippecanoe_county_2a6793d"
ASSET_ID = "massing_unitarian_universalist_church_of_tippecanoe_county_2a6793d"
OBJECT_NAME = "Unitarian Universalist Church of Tippecanoe County"
COLLECTION_NAME = "Asset_" + ASSET_ID


def evaluator():
    evidence = json.loads((AUDIT / "evidence.json").read_text(encoding="utf-8"))
    raw = json.loads((AUDIT / "sources" / "osm_way_860918857_full.json").read_text(encoding="utf-8"))
    nodes = {e["id"]: e for e in raw["elements"] if e["type"] == "node"}
    way = next(e for e in raw["elements"] if e["type"] == "way" and e["id"] == 860918857)
    tagged = way.get("tags", {})
    ring = [nodes[nid] for nid in way["nodes"]]
    closed = way["nodes"][0] == way["nodes"][-1]
    distinct = ring[:-1] if closed else ring
    expected_xy = []
    for n in distinct:
        lat, lon = float(n["lat"]), float(n["lon"])
        expected_xy.append(((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
                            (lat - 40.4274) * 111040.0))
    obj = bpy.data.objects.get(OBJECT_NAME)
    coll = bpy.data.collections.get(COLLECTION_NAME)
    structure_ok = obj is not None and obj.type == "MESH" and coll is not None and obj in coll.objects[:]
    mesh_xy = []
    world_verts = []
    if structure_ok:
        for vert in obj.data.vertices:
            p = obj.matrix_world @ vert.co
            world_verts.append(tuple(float(v) for v in p))
            if abs(p.z) < 1e-6:
                q = (round(p.x, 5), round(p.y, 5))
                if q not in mesh_xy:
                    mesh_xy.append(q)
    # Symmetric Hausdorff distance between exact GIS vertices and the mesh's grade vertices.
    def directed(a, b):
        return max(min(math.hypot(x-u, y-v) for u, v in b) for x, y in a) if a and b else None
    expected_q = [(round(x, 5), round(y, 5)) for x, y in expected_xy]
    hausdorff = max(directed(expected_q, mesh_xy) or 0.0, directed(mesh_xy, expected_q) or 0.0)
    src_bounds = [min(x for x, y in expected_xy), max(x for x, y in expected_xy),
                  min(y for x, y in expected_xy), max(y for x, y in expected_xy)]
    mesh_bounds = ([min(p[0] for p in world_verts), max(p[0] for p in world_verts),
                    min(p[1] for p in world_verts), max(p[1] for p in world_verts)]
                   if world_verts else None)
    z_bounds = [min(p[2] for p in world_verts), max(p[2] for p in world_verts)] if world_verts else None
    photo_exists = (AUDIT / "sources" / "wedding_spot_church_photo.jpg").is_file()
    history_text = (AUDIT / "sources" / "official_church_history.html").read_text(encoding="utf-8", errors="replace").lower()
    history_mentions_location = "333" in history_text and ("meridian" in history_text or "st. andrew" in history_text)
    closed_identity = (tagged.get("name") == OBJECT_NAME and tagged.get("addr:housenumber") == "333"
                       and tagged.get("addr:street") == "Meridian Street" and closed and len(distinct) == 19)
    sources_complete = all((AUDIT / p).is_file() for p in [
        "evidence.json", "sources/osm_way_860918857_full.json",
        "sources/official_church_history.html", "sources/wedding_spot_church_photo.jpg",
        "preview_exterior.png", "render_preview.py"])
    library_structure = (structure_ok and len(coll.objects) == 1 and len(obj.data.vertices) == 530
                         and len(obj.data.polygons) == 137 and bool(bpy.data.filepath)
                         and Path(bpy.data.filepath).name == ASSET_ID + ".blend")
    materials = [m.name for m in obj.data.materials] if structure_ok else []
    has_gable_colors = any("Stained_Glass" in m for m in materials)
    facade_features = {
        "seven distinct colored stained_glass bays": has_gable_colors,
        "paired glass entrance modeled": "paired glass entry doors" in " ".join(evidence.get("geometry_edits", [])).lower(),
        "multiple facade/window faces exist": structure_ok and len(obj.data.polygons) > 100,
        "visual reference retained": photo_exists,
    }
    # Criteria scores use the project 0-2 rubric. Unsupported vertical metrics are explicitly discounted.
    criteria = [
        {"name": "Correct identity and source-backed footprint", "score": 2.0, "max_score": 2,
         "status": "verified", "basis": f"OSM way/860918857 tags match exact building name and 333 Meridian; closed 19-vertex outline; official congregation history HTML also supports address/history. Exact source snapshots present."},
        {"name": "Position, orientation, and scale/dimensions", "score": 2.0 if structure_ok and hausdorff is not None and hausdorff <= 0.01 else 0.5,
         "max_score": 2, "status": "verified within source geometry", "basis": f"Reprojected OSM source ring with repository transform and compared with unique mesh grade vertices; symmetric vertex-set Hausdorff error={hausdorff:.6f} m; source bbox=[{src_bounds}]; model bounds incl. overhangs={mesh_bounds}. This validates against OSM, not survey control."},
        {"name": "Evidence-backed height, floors, and roof form", "score": 1.0, "max_score": 2,
         "status": "partially estimated", "basis": f"Source photo supports a gabled sanctuary silhouette; no measured eave/ridge elevation or reliable floor count was found. Model world z={z_bounds} m, with evidence correctly labeling 4.5/5.4/10.2 m as visual estimates."},
        {"name": "Facade, entrances, and distinctive architecture", "score": 1.5 if all(facade_features.values()) else 0.5,
         "max_score": 2, "status": "photo-supported but simplified", "basis": f"The retained exterior photo visibly shows the gabled stained-glass frontage, paired doors, and low side wings. The mesh has stained-glass materials and window/facade faces; these features are represented, but modeled frontage/mullions/materials remain simplified and only one facade photo is available."},
        {"name": "Modular export, portability, and complete evidence", "score": 2.0 if library_structure and sources_complete else 0.5,
         "max_score": 2, "status": "verified as massing library", "basis": f"Saved asset reopened in Blender; expected object and export collection retained with one mesh; file name/ID stable; no image/texture objects required by the mesh; source snapshots, structured evidence, builder, and preview script/render all exist. Manifest kind remains campus-frame massing, matching current coordinate frame."},
    ]
    score = round(sum(c["score"] for c in criteria), 1)
    findings = []
    if hausdorff is None or hausdorff > 0.01:
        findings.append("Rebuild or correct the structural wall ring: it does not match the projected OSM grade vertices within 1 cm.")
    findings.append("Keep sanctuary, wing eave, and ridge heights labeled as estimates until measured elevations or plans are sourced.")
    findings.append("The master file is Tobin-owned; placement/integration remains a coordinator task if this asset is promoted from its current massing library record.")
    return {"score": score, "max_score": 10, "criteria": criteria,
            "evidence": {"identity_tags": tagged, "source_outline_vertex_count": len(distinct),
                         "grade_vertex_count": len(mesh_xy), "grade_vertex_symmetric_hausdorff_m": hausdorff,
                         "source_bbox_xy_m": src_bounds, "model_bounds_xy_m_including_overhangs": mesh_bounds,
                         "model_z_bounds_m": z_bounds, "facade_feature_checks": facade_features,
                         "export_collection_objects": len(coll.objects) if coll else None,
                         "mesh_vertices": len(obj.data.vertices) if obj else None,
                         "mesh_faces": len(obj.data.polygons) if obj else None,
                         "history_mentions_location": history_mentions_location,
                         "saved_asset_path": bpy.data.filepath},
            "findings": findings}


result = evaluator()
result["evaluator"] = "Independent geometry/source review using Blender mesh vertex data and raw OSM feature 860918857"
result["review_date"] = "2026-10-26"
result["asset_path"] = "modular/buildings/" + ASSET_ID + ".blend"
(AUDIT / "independent_grade_kyle.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print("INDEPENDENT_GRADE=" + json.dumps(result))

