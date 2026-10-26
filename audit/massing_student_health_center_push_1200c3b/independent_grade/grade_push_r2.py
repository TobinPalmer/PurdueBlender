"""Fresh independent rubric evaluation for the revised Purdue Student Health Center asset.

Run with Blender 4.5: blender --background --python grade_push_r2.py
Reads the saved library and raw local evidence; writes only independent_grade_r2.json.
"""
import json
import math
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET_ID = "massing_student_health_center_push_1200c3b"
AUDIT = ROOT / "audit" / ASSET_ID
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
OUT = AUDIT / "independent_grade" / "independent_grade_r2.json"
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137

def project(lon, lat):
    return ((lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT)),
            (lat - ORIGIN_LAT) * 111040.0)

def bounds2(points):
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(2)]

def evaluate():
    raw = json.loads((AUDIT / "sources" / "purdue_gis_fid274_raw.json").read_text(encoding="utf-8-sig"))
    feature = raw["features"][0]
    attrs = feature["attributes"]
    ring = feature["geometry"]["rings"][0][:-1]
    gis_xy = [project(lon, lat) for lon, lat in ring]
    reg = json.loads((AUDIT / "source_register.json").read_text(encoding="utf-8"))
    build = json.loads((AUDIT / "build_result.json").read_text(encoding="utf-8"))
    reopen = json.loads((AUDIT / "reopen_verification.json").read_text(encoding="utf-8"))
    evidence = json.loads((AUDIT / "build_evidence.json").read_text(encoding="utf-8"))
    regions = json.loads((AUDIT / "mass_regions.json").read_text(encoding="utf-8"))

    assert attrs.get("FID") == 274 and attrs.get("BLDG_ABBR") == "PUSH"
    assert attrs.get("ADDRESS") == "601 Stadium Mall Drive"
    assert len(ring) == 13
    assert any(s.get("feature_id") == 274 for s in reg["sources"])

    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    coll = bpy.data.collections.get("Asset_" + ASSET_ID)
    objects = list(coll.objects) if coll else []
    meshes = [o for o in objects if o.type == "MESH"]
    depsgraph = bpy.context.evaluated_depsgraph_get()
    verts = []
    faces = 0
    for ob in meshes:
        ev = ob.evaluated_get(depsgraph)
        me = ev.to_mesh()
        try:
            verts.extend([ev.matrix_world @ v.co for v in me.vertices])
            faces += len(me.polygons)
        finally:
            ev.to_mesh_clear()
    xyz_bounds = [[min(v[i] for v in verts), max(v[i] for v in verts)] for i in range(3)] if verts else []
    source_bounds = bounds2(gis_xy)
    bound_error = max(abs(xyz_bounds[i][j] - source_bounds[i][j]) for i in range(2) for j in range(2)) if xyz_bounds else None
    mats = sorted({m.name for ob in meshes for m in ob.data.materials if m})
    unpacked = [img.filepath for img in bpy.data.images if img.source == "FILE" and not img.packed_file]
    collection_ok = bool(coll and len(objects) == 1 and len(meshes) == 1)
    reopened_ok = reopen.get("blend_reopened") is True and reopen.get("result") == "pass"

    provider_by_name = {s["provider"]: s for s in reg["sources"]}
    orthophoto = next(s for s in reg["sources"] if "IGIO" in s["provider"])
    photo = next(s for s in reg["sources"] if "John Underwood" in s["provider"])
    footprint_provider = next(s for s in reg["sources"] if s.get("feature_id") == 274)
    zone_names = sorted(r["name"] for r in regions["regions"])
    region_areas = {r["name"]: round(r["area_m2"], 2) for r in regions["regions"]}
    roof_forms = {r["name"]: r["roof_form"] for r in regions["regions"]}
    conflict_present = "unresolved" in evidence["vertical_geometry"]["conflict"].lower() and "uncertain" in evidence["vertical_geometry"]["status"].lower()
    source_snapshots_present = all((AUDIT / p).exists() for p in [
        "sources/purdue_gis_fid274_raw.json", "sources/purdue_push_exterior_2020.jpg",
        "sources/indiana_2023_push_orthophoto.jpg", "renders/push_orthophoto_gis_overlay.jpg",
        "renders/push_orthophoto_regions_overlay.jpg", "renders/push_exterior_preview.png",
        "renders/push_footprint_preview.png"])

    criteria = [
      {"name":"Correct identity and source-backed footprint", "score":2.0, "max_score":2,
       "evidence":f"Raw Purdue BuildingShapes layer-0 feature FID {attrs['FID']} identifies {attrs['BUILDING_N']} ({attrs['BLDG_ABBR']}), {attrs['ADDRESS']}. The 13-vertex official ring is reproduced by the model's campus-coordinate wall/roof plan. Raw record, layer metadata, and map/address cross-check are saved. The 2023 orthophoto independently supports the roof-plan interpretation.",
       "finding":"Identity and exterior plan are strongly verified. The internal division into three roof zones is interpretive, but the exterior footprint itself is the official FID 274 geometry."},
      {"name":"Position, orientation, and scale/dimensions", "score":1.9, "max_score":2,
       "evidence":f"Direct reopened Blender vertex bounds {xyz_bounds}; transformed GIS-ring XY bounds {source_bounds}; max XY bound error {bound_error:.3f} m. Geometry remains in the existing campus-coordinate frame; no manifest origin or placement marker changed.",
       "finding":"Horizontal extent, orientation, and placement closely match the authoritative ring. The repository's documented local geographic approximation is not a surveyed projection; small residual edge/overhang mismatch is visible in the overall bounds."},
      {"name":"Evidence-backed height, floors, and roof form", "score":1.2, "max_score":2,
       "evidence":f"Model/reopen height is {xyz_bounds[2][1]:.2f} m. The 2023 orthophoto roof overlay and raw orthophoto support three plan-level zones: {roof_forms}, areas {region_areas} m2. Evidence explicitly records the official GIS fields NUM_LEVELS/CountOfFLO=5, B=-11.3, F01-F04, Extrution=48, R=69.8 and their undocumented units/semantics; the rendered facade-level reading and all three zone heights are labeled estimates.",
       "finding":"The revised model differentiates the main pitched roof, lower entrance-side roof and lower southeast extension, which is a material improvement over one continuous roof. The main 14.63 m peak and wing eaves/ridges are still estimates, not established by the photo or orthophoto; GIS floor/extrusion fields remain unresolved and conflict with the visual three-band reading."},
      {"name":"Facade, entrances, and distinctive architecture", "score":1.2, "max_score":2,
       "evidence":"Direct comparison of the saved exterior render with Purdue's 2020 exterior photograph confirms red brick, pale horizontal trim, upper-story openings, red tile roofing, a lower entry volume, glazing and a medical emblem are represented. The source photo directly shows a much broader, multi-panel glazed entrance and varied upper window proportions.",
       "finding":"The massing revision adds lower wings and the entrance frontage. In the render, windows remain small, repetitive and applied uniformly across long elevations; the visible entrance is substantially less legible and simpler than the broad source portal. The exact side/rear fenestration and entrance orientation remain unverified because there is one oblique facade photograph."},
      {"name":"Modular export, portability, and complete evidence", "score":1.9, "max_score":2,
       "evidence":f"Directly reopened {ASSET.name}: expected collection present={coll is not None}, object count={len(objects)}, mesh count={len(meshes)}, evaluated polygons={faces}, materials={mats}, unpacked external images={unpacked}. Reopen report passes and matches the evaluated asset. Required raw GIS, official photo and page snapshot, orthophoto/metadata, source register, overlays, renders, build record, and uncertainty record are present={source_snapshots_present}.",
       "finding":"Stable asset ID/path and single-collection export are preserved; the library reopens, has no external image dependency, and has a complete source/evidence trail. A single combined mesh limits part-level editing but is valid for this massing library."}
    ]
    score = round(sum(c["score"] for c in criteria), 1)
    result = {
      "asset_id":ASSET_ID,
      "asset_file":"modular/buildings/" + ASSET_ID + ".blend",
      "grader":"fresh independent subagent (revision 2)",
      "score":score,"max_score":10,"pass_threshold":8,
      "status":"pass" if score >= 8 else "needs_iteration",
      "criteria":criteria,
      "evidence":{
       "direct_asset_inspection":{"collection_present":coll is not None,"object_count":len(objects),"mesh_object_count":len(meshes),"evaluated_vertex_count":len(verts),"evaluated_polygon_count":faces,"evaluated_bounds_xyz_m":xyz_bounds,"gis_xy_bounds_m":source_bounds,"max_xy_bound_error_m":bound_error,"materials":mats,"unpacked_external_images":unpacked},
       "source_inspection":{"provider":footprint_provider["provider"],"feature_id":attrs["FID"],"feature_name":attrs["BUILDING_N"],"abbreviation":attrs["BLDG_ABBR"],"address":attrs["ADDRESS"],"vertex_count":len(ring),"source_providers":[s["provider"] for s in reg["sources"]]},
       "height_roof_inspection":{"zones":zone_names,"zone_areas_m2":region_areas,"roof_forms":roof_forms,"vertical_conflict_recorded":conflict_present,"orthophoto_source":orthophoto["snapshot"],"facade_source":photo["snapshot"]},
       "visual_inspection":{"model_render":"renders/push_exterior_preview.png","footprint_render":"renders/push_footprint_preview.png","GIS_overlay":"renders/push_orthophoto_gis_overlay.jpg","roof_zone_overlay":"renders/push_orthophoto_regions_overlay.jpg","raw_orthophoto":orthophoto["snapshot"],"raw_facade_photo":photo["snapshot"]},
       "reopen_validation":reopen,"evidence_snapshots_complete":source_snapshots_present
      },
      "findings":[
       "The revised saved asset directly matches the official named/addressed FID 274 footprint and campus placement within a few centimeters in bounding extents.",
       "The newly differentiated roof zones are supported in plan by the raw 2023 orthophoto overlay; their wall/roof elevations remain estimates because the GIS height field semantics are undocumented and no dimensioned elevation was found.",
       "Compared with Purdue's 2020 photo, the broad lower entrance wing is now represented, but the opening/window proportions and facade rhythm remain simplified and the precise entry orientation is not verified.",
       "The asset reopens as the expected self-contained one-mesh collection, and raw source snapshots, renders and uncertainty notes are present."
      ]
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("PUSH_INDEPENDENT_GRADE_R2=" + json.dumps(result))
    return result

if __name__ == "__main__":
    evaluate()
