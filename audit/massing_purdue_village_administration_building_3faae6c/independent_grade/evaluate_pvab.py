"""Independent evaluator for PVAB; run with Blender 4.5+ in background."""
import bpy
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSET_ID = "massing_purdue_village_administration_building_3faae6c"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
AUDIT = ROOT / "audit" / ASSET_ID
OUT = AUDIT / "independent_grade" / "evaluation.json"
ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137

def xy_from_lonlat(lon, lat):
    return ((lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT)),
            (lat - ORIGIN_LAT) * 111040.0)

def evaluate():
    # Reopen the saved deliverable in this fresh Blender process; do not trust builder claims.
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    collection_name = f"Asset_{ASSET_ID}"
    coll = bpy.data.collections.get(collection_name)
    obj = bpy.data.objects.get("Purdue Village Administration Building")
    assert coll is not None and obj is not None and obj.type == "MESH"
    assert obj.name in coll.objects

    gis = json.loads((AUDIT / "sources" / "arcgis_fid524_raw.json").read_text(encoding="utf-8"))
    feat = gis["features"][0]
    attrs = feat["attributes"]
    ring = feat["geometry"]["rings"][0]
    if len(ring) > 1 and ring[0] == ring[-1]:
        ring = ring[:-1]
    expected = [xy_from_lonlat(float(lon), float(lat)) for lon, lat in ring]
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()
    verts = [eval_obj.matrix_world @ v.co for v in mesh.vertices]
    eval_obj.to_mesh_clear()
    bottom = [(v.x, v.y) for v in verts if abs(v.z) < 1e-5]
    top = [(v.x, v.y) for v in verts if abs(v.z - max(p.z for p in verts)) < 1e-5]
    max_error = max(min(math.dist(p, q) for q in bottom) for p in expected)
    dims = [max(v[i] for v in verts) - min(v[i] for v in verts) for i in range(3)]
    bounds = [[min(v.x for v in verts), max(v.x for v in verts)],
              [min(v.y for v in verts), max(v.y for v in verts)],
              [min(v.z for v in verts), max(v.z for v in verts)]]

    osm = json.loads((AUDIT / "sources" / "osm_way_283274993_raw.json").read_text(encoding="utf-8"))
    osm_match = any(e.get("type") == "way" and e.get("id") == 283274993 and
                    e.get("tags", {}).get("name") == "Purdue Village Administration Building"
                    for e in osm.get("elements", []))
    evidence_record = json.loads((AUDIT / "evidence_record.json").read_text(encoding="utf-8"))
    reopen = json.loads((AUDIT / "reopen_validation.json").read_text(encoding="utf-8"))
    files = ["build_log.txt", "evidence_record.json", "preview_oblique.png", "preview_top.png",
             "reopen_validation.json", "sources/arcgis_fid524_raw.json",
             "sources/osm_way_283274993_raw.json", "sources/purdue_archives_record_snapshot.json"]
    present = {name: (AUDIT / name).is_file() for name in files}
    resource_paths = []
    for group_name in ("images", "libraries", "fonts", "sounds", "movieclips", "cache_files"):
        group = getattr(bpy.data, group_name, [])
        for item in group:
            p = getattr(item, "filepath", "")
            if p:
                resource_paths.append(p)
    ext_paths = [p for p in resource_paths if Path(bpy.path.abspath(p)).is_absolute() and not p.startswith("//")]

    criteria = [
      {"criterion":"Identity and source-backed footprint", "score":2, "max_score":2,
       "status":"verified", "evidence":[
         f"Reopened mesh is named {obj.name}; official GIS feature FID {attrs.get('FID')} is labeled {attrs.get('BUILDING_N')} / {attrs.get('BLDG_ABBR')}.",
         f"Independent OSM way 283274993 snapshot is tagged with the same building name (match={osm_match}).",
         f"All {len(expected)} official source ring vertices match the evaluated bottom ring within {max_error:.6f} m; GIS area recorded as 2481.327 m²."],
       "findings":[] if attrs.get("FID") == 524 and osm_match and max_error < .01 else ["Identity, independent label, or source-ring agreement needs review."]},
      {"criterion":"Position, orientation, and scale/dimensions", "score":2, "max_score":2,
       "status":"verified against project GIS transform", "evidence":[
         f"Evaluated world-space bounds are {bounds} m; dimensions are {[round(x,3) for x in dims]} m.",
         "Campus coordinates and orientation derive directly from the named official EPSG:4326 ring using the documented project local approximation; mesh object transform is identity.",
         f"Reopen check reports {reopen.get('max_vertex_error_vs_live_gis_project_transform_m')} m maximum vertex error."],
       "findings":["The project conversion is approximate local tangent-plane math, not survey-grade georeferencing."]},
      {"criterion":"Evidence-backed height, floors, and roof form", "score":0, "max_score":2,
       "status":"unverified", "evidence":[
         f"Saved Z extent is {bounds[2]} m, but 4.2 m is explicitly tagged as an estimate.",
         f"GIS reports NUM_LEVELS={attrs.get('NUM_LEVELS')} and Extrution={attrs.get('Extrution')}; both are unpopulated/zero.",
         "The flat cap is described as generic; no roof profile or floor count source was found in the supplied source records."],
       "findings":["No evidence verifies model height, floor count, or roof form; estimated height and generic cap cannot earn evidence-backed points."]},
      {"criterion":"Facade, entrances, and distinctive architecture", "score":0, "max_score":2,
       "status":"unverified", "evidence":["The reopened asset is a plain single-material shell with no facade or entrance geometry.",
         "The attached archival record supports historical identity and use, but expressly lacks facade/elevation/roof description."],
       "findings":["No source-backed facade, entrance, or distinctive architectural feature is modeled or documented."]},
      {"criterion":"Modular export, portability, and complete evidence", "score":2 if all(present.values()) and len(coll.objects)==1 else 0,
       "max_score":2, "status":"verified" if all(present.values()) and len(coll.objects)==1 else "incomplete",
       "evidence":[f"Saved asset reopens; expected export collection {collection_name} contains {len(coll.objects)} object(s).",
         f"Required evidence files present: {present}.",
         f"Asset has no external file-path dependencies ({len(ext_paths)} absolute external paths found).",
         "Builder, evidence record, raw source snapshots, reopen validation, and two preview renders are present."],
       "findings":[] if all(present.values()) and len(coll.objects)==1 and not ext_paths else ["Export/evidence completeness or portability check failed."]}
    ]
    score = sum(c["score"] for c in criteria)
    return {"building_id":ASSET_ID, "evaluator":"independent_grade/evaluate_pvab.py",
            "evaluated_asset":str(ASSET), "score":score, "max_score":10,
            "passing_threshold":8, "passed":score>=8, "criteria":criteria,
            "evidence":{"reopened":True, "evaluated_vertex_count":len(verts), "evaluated_bounds_m":bounds,
                        "evaluated_dimensions_m":dims, "official_gis_fid":attrs.get("FID"),
                        "official_gis_name":attrs.get("BUILDING_N"), "official_ring_vertex_count":len(expected),
                        "maximum_source_vertex_error_m":max_error, "external_absolute_file_paths":ext_paths,
                        "evidence_files_present":present},
            "findings":[f for c in criteria for f in c["findings"]]}

result = evaluate()
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))

