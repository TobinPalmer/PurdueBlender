"""Independent Smith Hall evaluation for Kyle's asset revision; run with Blender --background."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSET_ID = "massing_smith_hall_4c2018f"
BLEND = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
EVIDENCE = HERE / "evidence.json"
RAW = HERE / "source_feature_249_raw.json"
PREVIEW = HERE / "preview_detail.png"

def evaluate():
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8-sig"))
    raw = json.loads(RAW.read_text(encoding="utf-8-sig"))
    attrs = raw["attributes"]
    ring = raw["geometry"]["rings"][0]
    if ring[0] == ring[-1]:
        ring = ring[:-1]
    lat0 = 40.4274
    source_xy = [((lon + 86.9137) * 111412.84 * math.cos(math.radians(lat0)),
                  (lat - lat0) * 111040.0) for lon, lat in ring]
    src_bbox = [min(p[0] for p in source_xy), max(p[0] for p in source_xy),
                min(p[1] for p in source_xy), max(p[1] for p in source_xy)]
    obj = bpy.data.objects.get("Smith Hall")
    coll = bpy.data.collections.get("Asset_" + ASSET_ID)
    if obj is None or coll is None:
        raise RuntimeError("Expected object or exported collection is missing")
    world = [obj.matrix_world @ v.co for v in obj.data.vertices]
    model_bbox = [min(v.x for v in world), max(v.x for v in world),
                  min(v.y for v in world), max(v.y for v in world)]
    model_z = [min(v.z for v in world), max(v.z for v in world)]
    bbox_delta = [model_bbox[i] - src_bbox[i] for i in range(4)]
    abs_delta = [abs(x) for x in bbox_delta]
    collection_objects = [o.name for o in coll.objects]
    sources_ok = (attrs.get("FID") == 249 and attrs.get("BLDG_ABBR") == "SMTH"
                  and attrs.get("BUILDING_N") == "Smith Hall" and len(ring) == 46)
    criteria = [
        {"name":"Correct identity and source-backed footprint", "score":2.0 if sources_ok else 0.0, "max_score":2,
         "evidence":f"Raw Purdue BuildingShapes feature FID={attrs.get('FID')}, code={attrs.get('BLDG_ABBR')}, name={attrs.get('BUILDING_N')}; {len(ring)} distinct official EPSG:4326 ring vertices. Builder rebuilds shell from that ring; GIS source is official but not survey-grade."},
        {"name":"Position, orientation, and scale/dimensions", "score":1.75 if max(abs_delta) <= 0.5 else (1.0 if max(abs_delta) <= 2 else 0.5), "max_score":2,
         "evidence":f"Recomputed source-ring bbox via repository transform: {src_bbox}; saved mesh world XY bbox: {model_bbox}; edge deltas (m): {bbox_delta}. Facade additions slightly extend the shell; exact footprint polygon shape cannot be reconstructed from aggregate bbox alone."},
        {"name":"Evidence-backed height, floors, and roof form", "score":1.0 if attrs.get("NUM_LEVELS") == 3 and abs(model_z[1]-12.0)<0.01 else 0.5, "max_score":2,
         "evidence":f"Source GIS reports {attrs.get('NUM_LEVELS')} levels and an Extrution field of {attrs.get('Extrution')} with no published units. Mesh height is {model_z[1]-model_z[0]:.2f} m, set to 12 m by estimating from floors; no measured elevation or explicit roof-form source is recorded. Preview shows a flat roof."},
        {"name":"Facade, entrances, and distinctive architecture", "score":1.75, "max_score":2,
         "evidence":"Preview shows red brick walls, three rows of repeated windows, a paired entrance with stone surround/lintel, and flat roof. Purdue Events source snapshot is an independent photo reference for brick facade and entrance, but window spacing and dimensions remain approximate."},
        {"name":"Modular export, portability, and complete evidence", "score":2.0 if len(collection_objects)==1 and PREVIEW.exists() and BLEND.exists() else 1.0, "max_score":2,
         "evidence":f"Saved source library reopens in Blender; expected collection contains {len(collection_objects)} object(s): {collection_objects}. Dedicated builder, config, raw GIS snapshot, captured Purdue Events page/photo, structured evidence, and preview are present. No external texture dependency is required."}
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    findings = [
        "12 m is an estimate based on the three-level GIS attribute; the source's Extrution=26 is undocumented here and should be investigated before claiming a verified height.",
        "No measured facade dimensions or roof plans were found; keep the roof, window rhythm, and entrance dimensions marked approximate.",
        "The modeled shell follows the official feature ring; small bbox differences come from doorway/facade additions and the source is not a certified survey."
    ]
    result = {"score":score,"max_score":10,"criteria":criteria,
              "evidence":{"blend_path":str(BLEND.relative_to(ROOT)),"render_path":str(PREVIEW.relative_to(ROOT)),
                          "reopened_in_blender":True,"source_feature_id":attrs.get("FID"),
                          "source_ring_vertices":len(ring),"source_bbox_xy_m":src_bbox,
                          "model_bbox_xy_m":model_bbox,"bbox_delta_m":bbox_delta,
                          "model_z_m":model_z,"collection_objects":collection_objects},
              "findings":findings}
    out = HERE / "independent_grade_kyle.json"
    out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))
    return result

evaluate()
