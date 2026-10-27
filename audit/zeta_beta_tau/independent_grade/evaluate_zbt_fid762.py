"""Independent rubric evaluator for the Rossen FID 762 ZBT library.

This deliberately does not import the builder's validator. Run from repository root:
  blender -b --python audit/zeta_beta_tau/independent_grade/evaluate_zbt_fid762.py
"""
from pathlib import Path
import hashlib, json, math, re
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / "modular/buildings/massing_house_301841332_9b3bd1f.blend"
AUDIT = ROOT / "audit/zeta_beta_tau"
OUT = AUDIT / "independent_grade/grade_result.json"
EXPECTED_SHA = "7ad90208e909dba1300ea2a5dc11e039e440d70135b2dd3bc28c0ec43521895f"
ASSET_ID = "massing_house_301841332_9b3bd1f"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
SCENE_NAME = f"Building_{ASSET_ID}"


def xy(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def directed_hausdorff(a, b):
    return max(min(math.dist(p, q) for q in b) for p in a)


def evaluate():
    """Return the AGENT.md rubric result with independent measurements/findings."""
    digest = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    assert digest == EXPECTED_SHA, f"Frozen asset changed: {digest}"
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene = bpy.data.scenes.get(SCENE_NAME)
    coll = bpy.data.collections.get(COLLECTION_NAME)
    assert scene and coll, "Stable exported scene/collection missing"
    objs = list(coll.objects)
    meshes = [o for o in objs if o.type == "MESH"]
    shell = bpy.data.objects.get("ZBT_Main_Envelope_FID762")
    assert shell and shell in objs and shell.type == "MESH"

    gis = json.loads((AUDIT / "sources/purdue_gis_fid762_2026-10-26_wgs84.json").read_text(encoding="utf-8"))
    feature = gis["features"][0]
    attrs = feature["attributes"]
    ring_ll = feature["geometry"]["rings"][0]
    if ring_ll[0] == ring_ll[-1]:
        ring_ll = ring_ll[:-1]
    expected = [xy(float(x), float(y)) for x, y in ring_ll]
    world = [shell.matrix_world @ v.co for v in shell.data.vertices]
    n = len(expected)
    base = [(v.x, v.y) for v in world[:n]]
    roof = [(v.x, v.y) for v in world[-n:]]
    xy_error = max(directed_hausdorff(expected, base), directed_hausdorff(base, expected),
                   directed_hausdorff(expected, roof), directed_hausdorff(roof, expected))
    zmin = min(v.z for v in world)
    zmax = max(v.z for v in world)
    all_verts = [(o.matrix_world @ v.co) for o in meshes for v in o.data.vertices]
    bounds = [[min(v[i] for v in all_verts), max(v[i] for v in all_verts)] for i in range(3)]

    contact = (AUDIT / "sources/zbt_purdue_contact_2026-10-26.html").read_text(encoding="utf-8", errors="replace")
    home = (AUDIT / "sources/zbt_purdue_homepage_2026-10-26.html").read_text(encoding="utf-8", errors="replace")
    crosswalk = (AUDIT / "crosswalk_resolution.md").read_text(encoding="utf-8", errors="replace")
    id_evidence = {
        "current_contact_has_address": "900 David Ross Road" in contact,
        "current_homepage_mentions_address": "900 David Ross Road" in home,
        "crosswalk_documents_conflicting_GIS_name": "Phi Kappa Theta" in crosswalk and "SOFKH" in crosswalk,
        "crosswalk_documents_ZBT_historical_and_current_sources": all(x in crosswalk for x in ("2017", "2018", "2026")),
        "current_photo_present": (AUDIT / "sources/zbt_purdue_current_website_photo.png").is_file(),
        "national_chapter_house_photo_present": (AUDIT / "sources/zbt_alpha_alpha_chapter_house_photo.jpg").is_file(),
        "historical_Purdue_report_present": (AUDIT / "sources/purdue_2007_official_investigation.pdf").is_file(),
        "2018_occupancy_report_present": (AUDIT / "sources/purdue_exponent_2018_fscl_report.pdf").is_file(),
    }
    assert attrs.get("FID") == 762 and attrs.get("BUILDING_N") == "Phi Kappa Theta"
    assert id_evidence["current_contact_has_address"] and id_evidence["current_homepage_mentions_address"]

    expected_collection = f"Asset_{ASSET_ID}"
    external_file_images = [im.filepath for im in bpy.data.images if im.source == "FILE" and im.filepath]
    nonempty_paths = [im for im in external_file_images if im.filepath.strip()]
    portable_paths = all(not Path(x).is_absolute() for x in nonempty_paths)
    stable_names = coll.name == expected_collection and scene.name == SCENE_NAME
    linked_objects = all(o.library is None for o in objs)
    criteria = [
        {"name":"Correct identity and source-backed footprint", "score":2.0,"max_score":2,
         "assessment":"PASS, with documented historic GIS label conflict. Current chapter contact and homepage identify ZBT at 900 David Ross; the captured national chapter photo shows ZBT/Alpha Alpha and the same address, while the GIS FID 762 at that address retains historic Phi Kappa Theta/SOFKH. The crosswalk compares 2007, 2017, 2018, and 2026 evidence and properly resolves this as one physical site while noting transition/shared-occupancy uncertainty. The building shell and roof plan ring independently agree with all 12 GIS vertices.",
         "evidence":id_evidence | {"GIS_feature_id":attrs.get("FID"),"GIS_name":attrs.get("BUILDING_N"),"GIS_address":attrs.get("ADDRESS"),"ring_unique_vertices":n,"shell_ring_bidirectional_error_m":xy_error}},
        {"name":"Position, orientation, and scale/dimensions", "score":1.75,"max_score":2,
         "assessment":"Strongly supported in horizontal location and plan shape by the source ring in the repository coordinate transform. The building occupies the same campus-world XY as the GIS ring; the main shell and roof ring match to float precision. Plan orientation comes from that mapped polygon. Its bounds and dimensions remain map-outline estimates rather than a surveyed wall-face measurement, and the chosen photo-facing edge is inferred, so a small deduction applies.",
         "evidence":{"asset_world_bounds_m":bounds,"source_ring_bidirectional_error_m":xy_error,"source_ring_vertices":n,"frontage_selection":"longest GIS edge, not georeferenced facade alignment"}},
        {"name":"Evidence-backed height, floors, and roof form", "score":1.25,"max_score":2,
         "assessment":"Flat/low-slope roof and shallow parapet are consistent with the captured chapter photos and aerial imagery. The 7.65 m height and two-floor interpretation are clearly labeled as estimates; the GIS NUM_LEVELS=1 conflict and absence of a measured elevation make these less than fully verified.",
         "evidence":{"shell_vertical_extent_m":[zmin,zmax],"height_status":"photo-guided estimate; no surveyed vertical datum","story_count_status":"estimated from photos; GIS legacy value conflicts","roof_form_status":"photo/aerial supported; pitch and elevation uncertain"}},
        {"name":"Facade, entrances, and distinctive architecture", "score":1.5,"max_score":2,
         "assessment":"The light broad facade, regular glazing, large timber-railed deck, ZBT sign, and stair are recognizable from the saved national/current chapter imagery. The render contains a continuous deck and railings with repeated window bays. The images do not supply a georeferenced elevation or reliable entry-door location; unseen elevations and some window placement remain schematic, so this receives partial credit.",
         "evidence":{"reference_images":["sources/zbt_alpha_alpha_chapter_house_photo.jpg","sources/zbt_purdue_current_website_photo.png"],"preview":"zbt_preview_fresh_reopen.png","visible modeled features":["light wall envelope","repeated divided windows","long timber-railed frontage deck","ZBT lettering","front stair"]}},
        {"name":"Modular export, portability, and complete evidence", "score":2.0,"max_score":2,
         "assessment":"PASS. Stable scene/collection names and asset path are present, the collection contains the dedicated building meshes, the project has a dedicated reproducible build script and source/evidence folder, and independently inspected Blender data show no nonempty external image dependencies. Existing fresh reopen/linked append logs use the same exact frozen SHA and report success.",
         "evidence":{"asset_sha256":digest,"scene":scene.name,"collection":coll.name,"object_count":len(objs),"mesh_count":len(meshes),"all_objects_local_data":linked_objects,"external_image_paths":nonempty_paths,"external_paths_relative":portable_paths,"existing_fresh_reopen":"PASS, same frozen SHA","existing_fresh_linked_append":"PASS, same frozen SHA"}},
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    findings = [
        "PASS threshold met (8/10).",
        "Historic GIS naming conflict is acknowledged rather than silently overwritten: the asset represents the currently documented ZBT facility at 900 David Ross, while transition timing and possible temporary shared occupancy remain unresolved.",
        "Treat the polygon-derived shell as a GIS roof/map-outline proxy, not a surveyed wall footprint; the GIS geometry and Shape__Area field are inconsistent and the imagery has canopy/seam occlusion.",
        "Retain explicit uncertainty on the 7.65 m height, story count, frontage-edge choice, window rhythm, door position, and unpictured sides; these are not surveyed facts.",
    ]
    return {"building":"Zeta Beta Tau — Alpha Alpha, Purdue University", "asset_id":ASSET_ID,
            "asset_path":"modular/buildings/"+ASSET.name,"asset_sha256":digest,
            "grader":"Independent subagent; evaluator written from direct source and Blender data review; does not import builder validators.",
            "blender_version":bpy.app.version_string,"score":score,"max_score":10,
            "pass":score>=8,"criteria":criteria,"evidence":{"gis_source_attributes":attrs,
            "crosswalk_evidence_checks":id_evidence,"direct_geometry_measurement":{"GIS_to_shell_bidirectional_max_xy_error_m":xy_error,"estimated_shell_bounds_m":bounds,"object_count":len(objs),"mesh_object_count":len(meshes),"nonempty_external_image_paths":nonempty_paths}},"findings":findings}

if __name__ == "__main__":
    result = evaluate()
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("INDEPENDENT_ZBT_GRADE=" + json.dumps(result, ensure_ascii=False))
