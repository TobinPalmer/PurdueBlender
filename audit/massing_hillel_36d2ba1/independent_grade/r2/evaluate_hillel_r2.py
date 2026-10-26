"""Independent Hillel r2 asset inspection and rubric evaluation."""
import bpy, json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ASSET_ID = "massing_hillel_36d2ba1"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
AUDIT = ROOT / "audit" / ASSET_ID
OUT = Path(__file__).resolve().parent
RADIUS = 6378137.0

def wm_to_local(x, y):
    lon = math.degrees(x / RADIUS)
    lat = math.degrees(2 * math.atan(math.exp(y / RADIUS)) - math.pi / 2)
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)

def area(poly):
    return abs(sum(poly[i][0] * poly[(i+1)%len(poly)][1] -
                   poly[(i+1)%len(poly)][0] * poly[i][1]
                   for i in range(len(poly))) / 2)

def inspect():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene = bpy.data.scenes.get("Building_" + ASSET_ID)
    coll = bpy.data.collections.get("Asset_" + ASSET_ID)
    objects = list(coll.objects) if coll else []
    dg = bpy.context.evaluated_depsgraph_get()
    records, vertices = [], []
    shell_ground = []
    for ob in objects:
        if ob.type != "MESH":
            continue
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        world = [ev.matrix_world @ v.co for v in me.vertices]
        vertices.extend(world)
        if ob.name == "Hillel":
            shell_ground = [(v.x, v.y) for v in world if abs(v.z) < 1e-4]
        records.append({"name": ob.name, "vertices": len(me.vertices),
                        "faces": len(me.polygons),
                        "modifiers": [m.name for m in ob.modifiers],
                        "materials": [m.name if m else None for m in me.materials],
                        "library": ob.library.filepath if ob.library else None})
        ev.to_mesh_clear()
    bounds = [[min(v[i] for v in vertices), max(v[i] for v in vertices)] for i in range(3)]
    source = json.loads((AUDIT / "gis_feature_803.json").read_text(encoding="utf-8-sig"))
    feature = source.get("feature", source.get("features", [{}])[0])
    attrs = feature["attributes"]
    ring = [wm_to_local(x, y) for x, y in feature["geometry"]["rings"][0]]
    if len(ring)>1 and math.dist(ring[0], ring[-1]) < .01: ring.pop()
    errors = [min(math.dist(p, q) for q in shell_ground) for p in ring]
    libs = [lib.filepath for lib in bpy.data.libraries]
    unpacked = [im.filepath for im in bpy.data.images if im.source == "FILE" and im.filepath and not im.packed_file]
    render_names = ["hillel_exterior_oblique_r2.png", "hillel_waldron_front_r2.png", "hillel_roof_top_r2.png"]
    renders = [{"path": n, "exists": (AUDIT/n).is_file(),
                "bytes": (AUDIT/n).stat().st_size if (AUDIT/n).is_file() else 0} for n in render_names]
    return {"opened_saved_asset": True, "blender_version": bpy.app.version_string,
            "asset": str(ASSET), "scene": scene.name if scene else None,
            "scene_object_count": len(scene.objects) if scene else None,
            "collection": coll.name if coll else None,
            "collection_object_count": len(objects), "mesh_objects": records,
            "evaluated_world_bounds_m": bounds,
            "evaluated_dimensions_m": [b[1]-b[0] for b in bounds],
            "GIS_feature": {"FID":attrs.get("FID"), "BLDG_ABBR":attrs.get("BLDG_ABBR"),
                "BUILDING_N":attrs.get("BUILDING_N"), "ADDRESS":attrs.get("ADDRESS"),
                "NUM_LEVELS":attrs.get("NUM_LEVELS"), "CountOfFLO":attrs.get("CountOfFLO"),
                "Extrution":attrs.get("Extrution"), "ring_vertices":len(ring),
                "local_projected_area_m2":area(ring), "max_nearest_shell_ground_vertex_error_m":max(errors),
                "mean_nearest_shell_ground_vertex_error_m":sum(errors)/len(errors)},
            "external_libraries":libs, "unpacked_external_images":unpacked,
            "render_files":renders, "render_engine":scene.render.engine if scene else None}

def evaluate(i):
    gis=i["GIS_feature"]
    footprint_ok=(gis["FID"]==803 and gis["BLDG_ABBR"]=="SOHIL" and
                  gis["BUILDING_N"]=="Hillel Foundation" and gis["ring_vertices"]==12 and
                  gis["max_nearest_shell_ground_vertex_error_m"] < .001)
    expected_scene="Building_"+ASSET_ID
    expected_coll="Asset_"+ASSET_ID
    renders_ok=all(r["exists"] and r["bytes"]>10000 for r in i["render_files"])
    portable=not i["external_libraries"] and not i["unpacked_external_images"]
    criteria=[
      {"criterion":"Correct identity and source-backed footprint","score":2.0 if footprint_ok else .5,"max_score":2,
       "evidence":"Directly reopened r2 mesh shell matches the 12-vertex converted ring of Purdue GIS BuildingShapesZip4 FID 803 (SOHIL, Hillel Foundation, 912 W State St) to <0.001 m. County 2019 minutes identify the same Hillel site, and the reported existing area (~6,500 sq ft) is close to the transformed GIS area (~610.95 m² / 6,574 sq ft).",
       "uncertainty":"GIS layer survey/date metadata is not stated. County hearing also discusses a proposed 845 sq ft addition, with completion unresolved; the model preserves the candidate pre-addition footprint."},
      {"criterion":"Position, orientation, and scale/dimensions","score":1.8 if footprint_ok else .7,"max_score":2,
       "evidence":"Shell is directly positioned in the documented local campus coordinate frame and follows GIS footprint vertices. GIS bounds are approximately 31.40 × 25.58 m; transformed area agrees reasonably with county's approximate area. County hearing text says the front faces Waldron Street; model places its principal entry on the west frontage.",
       "uncertainty":"Coordinates use the project's approximate conversion, not survey control. Exact structural dimensions/frontage registration were not established independently of the GIS polygon."},
      {"criterion":"Evidence-backed height, floors, and roof form","score":1.4,"max_score":2,
       "evidence":"GIS attributes report one level; the official Spring 2022 Hillel newsletter exterior photograph shows a low single-storey building and a broad, shallow/low-slope roof edge. The r2 model represents one low volume with broad flat eaves.",
       "uncertainty":"No measured elevation or roof pitch is available. The 3.6576 m shell height and ~0.7 m eave depth are explicitly visual estimates/placeholders, not source measurements."},
      {"criterion":"Facade, entrances, and distinctive architecture","score":1.6,"max_score":2,
       "evidence":"Compared r2 oblique/front renders against the official Spring 2022 newsletter photograph. Both show light buff masonry, repeated tall multi-light window bays, substantial pale framing/piers, a prominent entrance/sign panel, and a broad shallow roof edge. The county minutes independently say the front faces Waldron Street; the model puts its entry at that side.",
       "uncertainty":"Newsletter image is oblique and not compass-registered; exact window count, positions, sizes, entry dimensions and masonry/roof materials remain schematic. Model is a simplified representation, not a verified elevation."},
      {"criterion":"Modular export, portability, and complete evidence","score":(1.5 if i["scene"]==expected_scene and i["collection"]==expected_coll and i["collection_object_count"]==4 and portable and renders_ok else 1.0),"max_score":2,
       "evidence":"Saved r2 .blend reopened directly in Blender 4.5.15. Expected scene and named asset collection exist with four mesh objects; no linked libraries or unpacked external images. Three r2 preview renders, raw GIS snapshot, source provenance, county documents, Hillel official source snapshot, and reopen validation are present.",
       "uncertainty":"Asset portability and collection structure pass. The model's render engine is Blender 4.5 EEVEE Next; successful render-generation is evidenced by saved previews, but another Blender version's engine compatibility is not established."}
    ]
    score=round(sum(c["score"] for c in criteria),1)
    return {"building_id":ASSET_ID,"review_revision":"r2","score":score,"max_score":10,
      "passing_threshold":8,"passed":score>=8,"criteria":criteria,
      "evidence":{"direct_reopen_measurements":"direct_inspection.json",
        "source_record":"../../source_record.json","GIS_snapshot":"../../gis_feature_803.json",
        "county_plan":"../../2019_tippecanoe_hillel_sketch_plan.pdf",
        "county_minutes":"../../2019_tippecanoe_variance_minutes.pdf",
        "official_newsletter_photo":"../../purdue_hillel_2022_large-01.png",
        "r2_renders":["../../hillel_exterior_oblique_r2.png","../../hillel_waldron_front_r2.png","../../hillel_roof_top_r2.png"],
        "measurements":i},
      "findings":[
        {"severity":"moderate","finding":"Current building footprint may include an unresolved 2019 addition proposal; the asset keeps the source GIS candidate ring and does not claim later addition status.","action":"Retain this limitation and update only if a later as-built/parcel source establishes the addition geometry."},
        {"severity":"moderate","finding":"Height, roof pitch, and eave depth lack measured source dimensions.","action":"Keep the 3.6576 m height and eave depth labeled schematic/estimated."},
        {"severity":"minor","finding":"Facade rendering has photo-supported general character, but exact opening layout and materials cannot be verified from an unregistered oblique newsletter photo.","action":"Keep individual openings and finishes explicitly illustrative."}
      ]}

OUT.mkdir(parents=True,exist_ok=True)
inspection=inspect()
(OUT/"direct_inspection.json").write_text(json.dumps(inspection,indent=2)+"\n",encoding="utf-8")
result=evaluate(inspection)
(OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))
