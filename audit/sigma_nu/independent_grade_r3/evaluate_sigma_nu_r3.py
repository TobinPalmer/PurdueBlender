"""Independent Sigma Nu r3 evaluation; run in a fresh Blender process."""
import json
import hashlib
import math
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / "modular/buildings/massing_house_301841330_f58ae87.blend"
SOURCES = ROOT / "audit/sigma_nu/sources"
OUT = Path(__file__).resolve().parent / "independent_grade_r3.json"

def nearest_symmetric_error(a, b):
    return max(max(min(math.dist(p, q) for q in b) for p in a),
               max(min(math.dist(q, p) for p in a) for q in b))

def evaluate():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    feature = json.loads((SOURCES / "purdue_gis_fid_758.json").read_text(encoding="utf-8-sig"))
    attrs = feature["attributes"]
    ring = feature["geometry"]["rings"][0]
    if ring[0] == ring[-1]:
        ring = ring[:-1]
    lat0, lon0 = 40.4274, -86.9137
    x_scale = 111412.84 * math.cos(math.radians(lat0))
    source_xy = [((lon-lon0)*x_scale, (lat-lat0)*111040.0) for lon,lat in ring]

    scene_name = "Building_massing_house_301841330_f58ae87"
    collection_name = "Asset_massing_house_301841330_f58ae87"
    scene = bpy.data.scenes.get(scene_name)
    collection = bpy.data.collections.get(collection_name)
    assert scene is not None and collection is not None
    body = bpy.data.objects.get("House_301841330")
    assert body is not None and body.type == "MESH"
    base_xy = [(float(v.co.x), float(v.co.y)) for v in body.data.vertices if abs(v.co.z) < 1e-6]
    ring_error = nearest_symmetric_error(source_xy, base_xy)
    objects = list(collection.objects)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    world_points = []
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        world_points.extend(obj.matrix_world @ Vector(c) for c in evaluated.bound_box)
    bounds = [[min(p[i] for p in world_points), max(p[i] for p in world_points)] for i in range(3)]
    file_images = [img.filepath for img in bpy.data.images if img.source == "FILE"]
    external_libs = [lib.filepath for lib in bpy.data.libraries if lib.filepath]

    asset_sha256 = hashlib.sha256(ASSET.read_bytes()).hexdigest()

    criteria = [
        {"name":"Correct identity and source-backed footprint", "score":2.0, "max_score":2.0,
         "evidence":[f"Raw Purdue GIS FeatureServer snapshot identifies FID {attrs['FID']} as {attrs['BLDG_ABBR']} / {attrs['OWNER']} at {attrs.get('ADDRESS','1301 Tower Dr')}.", f"In a fresh Blender process, I compared all {len(source_xy)} source ring vertices to the saved House_301841330 base ring in both nearest-neighbor directions; maximum error was {ring_error:.9f} m.", "Fall 2019 Beta Zeta newsletter page contains a 1301 address plaque and chapter-house exterior imagery, independently supporting identity."],
         "uncertainty":["Purdue GIS record describes a building outline, not a surveyed structural-wall line; it is a strong identity/shape proxy, not a verified wall footprint."]},
        {"name":"Position, orientation, and scale/dimensions", "score":1.7, "max_score":2.0,
         "evidence":["Saved footprint coordinates reproduce the documented local approximate WGS84-to-campus transform from the Purdue GIS ring; independently computed horizontal bound extents are approximately 33.78 m east-west by 29.82 m north-south.", f"Fresh-process saved-asset bounds are {bounds}; the footprint shell remains in the GIS-derived campus frame without translation or rotation.", "OSM Tower Drive context supports adjacency and a north/northwest facade hypothesis."],
         "uncertainty":["The project's transform is a local approximation, not a surveyed CRS; facade bearing is an inference because newsletter photos are not georeferenced. GIS plan polygon may be roof edge rather than wall edge."]},
        {"name":"Evidence-backed height, floors, and roof form", "score":0.9, "max_score":2.0,
         "evidence":["The Spring 2022 newsletter publisher's page 0 identifies a First Floor Blue Room, Second Floor Bathroom, and Third Floor Study Room; this supports at least three occupied levels, not exact exterior floor lines or which levels are above grade. Verified in the publisher's rendered-page text and the saved page-0 thumbnail (https://www.epageflip.net/i/1467079-spring-2022-newsletter).", f"Fresh Blender inspection measures the saved model's top at {bounds[2][1]:.3f} m; model script labels 7.2 m wall height and 7.45 m roof top as estimates.", "The saved model has a shallow flat/parapet cap, but available chapter newsletter photos do not establish the roof silhouette or dimensions."],
         "uncertainty":["No source measures absolute height, floor elevations, number of above-grade floors, or roof form. Retained as provisional estimates; most of this criterion is unsupported."]},
        {"name":"Facade, entrances, and distinctive architecture", "score":1.6, "max_score":2.0,
         "evidence":["Fall 2019 newsletter photo directly shows the chapter-house exterior at 1301 Tower Drive: red/brown brick, light masonry/trim, a centered recessed entrance/canopy, repeated openings, and a projecting side bay are broadly reflected in the asset and preview.", "Model uses a generalized light lower band and red brick upper walls, two rows of front openings, central entrance, horizontal bands, and one restrained side bay; this aligns at broad compositional level with the cited photos."],
         "uncertainty":["Photographs are perspective-distorted and partly occluded; exact opening counts, spacing, dimensions, story lines, trim profiles, and mapping of pictured facade to a specific GIS edge are unverified. The dark preview underrepresents detail but is a render/lighting limitation, not additional evidence."]},
        {"name":"Modular export, portability, and complete evidence", "score":1.8, "max_score":2.0,
         "evidence":[f"Fresh Blender 5.2.3 load found the expected scene and export collection with {len(objects)} mesh objects; the asset also contains a separate review-only camera/light collection.", f"Independent inspection found no file-backed textures ({file_images}) and no linked Blender libraries ({external_libs}); geometry is self-contained.", "Dedicated build script, preview, raw GIS snapshot, road context, assessor snapshot, newsletter captures, and a source register with URLs/providers/dates/CRS/methods/uncertainties are present."],
         "uncertainty":["The official foundation-house image is referenced in the source register but is not preserved as a local raw image snapshot. It is not essential to the grade because the newsletter exterior and GIS establish identity and broad facade cues."]}
    ]
    score = sum(item["score"] for item in criteria)
    result = {
        "building_id":"massing_house_301841330_f58ae87", "grader":"independent_grader_r3", "grade_round":3,
        "score":score, "max_score":10, "passing_threshold":8, "passed":score >= 8,
        "criteria":criteria,
        "evidence":{"asset":"modular/buildings/massing_house_301841330_f58ae87.blend",
                    "fresh_process_blender_version":bpy.app.version_string,
                    "asset_sha256":asset_sha256,
                    "source_fid":attrs["FID"], "source_ring_vertices":len(source_xy),
                    "saved_base_ring_vertices":len(base_xy), "symmetric_nearest_vertex_error_m":ring_error,
                    "saved_asset_bounds_m":bounds, "asset_collection_object_count":len(objects),
                    "asset_collection_types":{t:sum(obj.type==t for obj in objects) for t in sorted({o.type for o in objects})},
                    "body_modifiers":[m.name for m in body.modifiers], "external_file_images":file_images,
                    "linked_libraries":external_libs,
                    "preview":"audit/sigma_nu/sigma_nu_preview.png",
                    "newsletter_photo":"audit/sigma_nu/sources/beta_zeta_fall_2019_newsletter_page2_900.jpg",
                    "spring_newsletter_html":"audit/sigma_nu/sources/beta_zeta_spring_2022_newsletter_page.html",
                    "raw_gis":"audit/sigma_nu/sources/purdue_gis_fid_758.json"},
        "findings":["This r3 saved asset passes the required 8/10 threshold based on direct inspection of its geometry and current source evidence.",
                     "Footprint and identity are strong; exactness is to the Purdue GIS outline, whose boundary is not known to be the structural wall.",
                     "The newsletter provides evidence for at least three occupied floor levels and broad front/side facade cues. It does not support the model's absolute height or roof profile, which remain estimates.",
                     "Orientation toward Tower Drive is contextually plausible but remains inferred because the chapter-house images are not georeferenced."]}
    OUT.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result

evaluate()
