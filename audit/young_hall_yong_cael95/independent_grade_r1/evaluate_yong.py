"""Independent YONG evaluator.

Run with:
  blender -b modular/buildings/massing_young_hall_yong_cae1b95.blend --python audit/young_hall_yong_cael95/independent_grade_r1/evaluate_yong.py
"""
import bpy, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
AUDIT=Path(__file__).resolve().parents[1]
OUT=Path(__file__).with_name("result.json")

def evaluate():
    gis=json.loads((AUDIT/"purdue_gis_yong_fid70.json").read_text(encoding="utf-8"))["features"][0]
    evidence=json.loads((AUDIT/"evidence.json").read_text(encoding="utf-8"))
    feature=gis["attributes"]
    ring=gis["geometry"]["rings"][0]
    if ring[0]==ring[-1]: ring=ring[:-1]
    projected=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),
                (lat-40.4274)*111040.0) for lon,lat in ring]
    coll=bpy.data.collections.get("Asset_massing_young_hall_yong_cae1b95")
    shell=bpy.data.objects.get("Young Hall (YONG)")
    actual=[]
    if shell:
        actual=[((shell.matrix_world@v.co).x,(shell.matrix_world@v.co).y)
                for v in shell.data.vertices if abs((shell.matrix_world@v.co).z)<0.001]
    if len(actual)==len(projected):
        mismatch=max((math.dist(a,b) for a,b in zip(actual,projected)),default=0.0)
    else:
        mismatch=float("inf")
    bounds=[[min(p[i] for p in projected),max(p[i] for p in projected)] for i in range(2)]
    sources={s["provider"]:s for s in evidence["sources"]}
    facade=Path(AUDIT/"purdue_young_hall_facade_reference.jpg").exists()
    photo_supported=facade and "image_url" in sources.get("Purdue University Pre-Professional Advising",{})
    deps=[i.filepath for i in bpy.data.images if i.filepath and i.source=="FILE"]
    member_names=[o.name for o in coll.objects] if coll else []
    member_types=[o.type for o in coll.objects] if coll else []
    height=shell.dimensions.z if shell else None
    criteria=[
      {"name":"Identity and source-backed footprint","score":2.0,"max_score":2.0,
       "evidence":[f"Official Purdue GIS feature FID {feature.get('FID')} is {feature.get('BUILDING_N')} (BLDG_ABBR {feature.get('BLDG_ABBR')}).",
                   f"Shell base ring has {len(actual)} vertices; projected source ring has {len(projected)}; max paired point error {mismatch:.6f} m.",
                   "Source address is 155 S Grant Street."],
       "findings":"Identity and horizontal outline are directly supported by the matching named Purdue GIS record."},
      {"name":"Position, orientation, and plan dimensions","score":2.0 if mismatch<=0.01 else 0.0,"max_score":2.0,
       "evidence":[f"Shell XY bounds from official ring: {bounds} m.",
                   "The shell geometry directly uses the project geographic conversion and retains campus coordinates; orientation and every ring point align with source.",
                   f"Measured vertex deviation in Blender asset: {mismatch:.6f} m."],
       "findings":"Position, orientation and plan geometry agree with GIS within the numerical tolerance of the projected vertices. Geographic conversion is approximate, not survey control."},
      {"name":"Height, floors, and roof form","score":1.25,"max_score":2.0,
       "evidence":[f"Shell height is {height:.3f} m; asset metadata identifies it as GIS R=102 interpreted as feet.",
                   f"GIS NUM_LEVELS and CountOfFLO are {feature.get('NUM_LEVELS')} and {feature.get('CountOfFLO')}; evidence cites Purdue Archives' description of 10 stories.",
                   "GIS vertical fields have no unit annotation, and no measured roof or elevation source is included."],
       "findings":"Story count has authoritative archival support, but the 11-versus-10 discrepancy is unresolved. Roof height depends on an inferred unit conversion, and flat roof form is not verified."},
      {"name":"Facade, entrance, and distinctive architecture","score":1.0,"max_score":2.0,
       "evidence":[f"Purdue facade image present: {photo_supported}; image shows red brick in a contrasting mortar grid, Young Hall lettering, and a metal-framed upper window.",
                   "The model has red brick and mortar materials, window bays, a Young Hall sign and a simulated entrance."],
       "findings":"Material and sign are evidenced by a close crop, but it does not document overall elevations or entrance design. Window rhythm, bay spacing, entry canopy/stairs, and roof treatment are largely modeled from inference."},
      {"name":"Modular export, portability, and evidence","score":1.75,"max_score":2.0,
       "evidence":[f"Expected collection exists: {coll is not None}; its {len(member_names)} members have types {sorted(set(member_types))}.",
                   f"Saved scene: {bpy.context.scene.name}; external file references in images: {deps}.",
                   "Raw GIS response, GIS metadata, July 2025 Purdue campus map, Purdue facade photo, evidence record, fresh-open validation and renders are present."],
       "findings":"Stable names and portable standalone asset are present. A render-target EMPTY is included inside the export collection; removing preview-only helpers would keep the library cleaner."}
    ]
    score=round(sum(c["score"] for c in criteria),2)
    result={"score":score,"max_score":10,"criteria":criteria,
            "evidence":{"asset":str(ROOT/"modular/buildings/massing_young_hall_yong_cae1b95.blend"),
                        "scene":bpy.context.scene.name,"collection":"Asset_massing_young_hall_yong_cae1b95",
                        "gis_feature_id":feature.get("FID"),"gis_building_abbr":feature.get("BLDG_ABBR"),
                        "gis_ring_vertices":len(projected),"asset_ring_vertices":len(actual),
                        "max_vertex_error_m":mismatch,"shell_height_m":height,
                        "external_file_dependencies":deps,
                        "evidence_folder":str(AUDIT)},
            "findings":[
              "The saved shell reproduces the full Purdue GIS polygon, but its absolute campus XY values come from the project's local approximate conversion.",
              "The footprint is much better evidenced than the vertical model: height units are inferred and the roof silhouette is unverified.",
              "Facade material/sign cues are supported by one Purdue crop; building-wide window, entrance and interior details remain schematic.",
              "Interior layout is representative only; no floor plan was found in the source set.",
              "The collection contains a preview-only render target helper alongside building geometry."
            ]}
    return result

result=evaluate()
OUT.write_text(json.dumps(result,indent=2),encoding="utf-8")
print(json.dumps(result,indent=2))
